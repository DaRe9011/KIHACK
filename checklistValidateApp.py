from flask import Flask, request, render_template, jsonify, url_for
import os
import pytesseract
from PIL import Image
import PyPDF2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import openai
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

uploaded_files_info = []


# Azure OpenAI Credentials
AZURE_OPENAI_ENDPOINT = "https://chris-m878n5co-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview"
AZURE_OPENAI_API_KEY = "AiggsQ1JmjsjBnSq2BqfFsFyS6y3YuGIxQs9KtOb2Xsyu1R4umR1JQQJ99BCACHYHv6XJ3w3AAAAACOGOZuN"
AZURE_DEPLOYMENT_NAME = "gpt-4o"  # The model name you deployed

# Initialize OpenAI client (Corrected)
client_openai = openai.AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2025-01-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT)

# client_openai = openai.Client(
#     api_key=AZURE_OPENAI_API_KEY,
#     base_url=f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_DEPLOYMENT_NAME}",
#     default_headers={"api-version": "2024-02-15"}
# )

# Azure Form Recognizer API credentials (Replace with your actual keys and endpoint)
AZURE_FORM_RECOGNIZER_KEY = "6U6qLo17r70YWbGQPgVX3ovHdWKLXjIMzijFECAAZNm3G6QWEbDdJQQJ99BCACYeBjFXJ3w3AAALACOGpIx4"
AZURE_FORM_RECOGNIZER_ENDPOINT = "https://btgkai.cognitiveservices.azure.com/"
# Set up the Azure Document Analysis Client
client = DocumentAnalysisClient(
    endpoint=AZURE_FORM_RECOGNIZER_ENDPOINT,
    credential=AzureKeyCredential(AZURE_FORM_RECOGNIZER_KEY)
)

# Function to extract text using Azure Form Recognizer (replaces old extract function)
def extract_text_from_file(file_path):
    """Extract text using Azure Form Recognizer (from image or PDF)."""
    try:
        with open(file_path, "rb") as f:
            # Analyze the document (prebuilt-document is the model that works with generic documents)
            poller = client.begin_analyze_document("prebuilt-document", f)
            result = poller.result()
            print("direct result",result)
            print(type(result))
            with open("results.json", "w", encoding="utf-8") as f:

                json.dump(dict(result), f, indent=4)

            # Extract text from the result (loop through pages and lines)
            extracted_text = ""
            for page in result.pages:
                for line in page.lines:
                    extracted_text += line.content + "\n"
            #print("extracted text:", extracted_text)
            return extracted_text

    except Exception as e:
        print(f"Error extracting text from file: {e}")
        return ""

def calculate_similarity(doc_text, checklist_description):
    """Calculate the cosine similarity between document text and checklist description."""
    vectorizer = CountVectorizer().fit_transform([doc_text, checklist_description])
    cosine_sim = cosine_similarity(vectorizer[0:1], vectorizer[1:2])
    return cosine_sim[0][0]


def validate_document(checklist_item, doc_text):
    """Use Azure OpenAI to validate document based on checklist items."""
    checkpoints = checklist_item.get('checkpoints', [])  # Ensure it's a list
    validation_results = []

    if not isinstance(checkpoints, list):
        print("Error: 'checkpoints' is not a list. Converting...")
        checkpoints = [checkpoints]  # Convert string to list

    for checkpoint in checkpoints:
        print(f"Checking checkpoint: {checkpoint} for Document Text.")

        prompt = f"Does the following text contain valid information for: '{checkpoint}'? Document Text: {doc_text}"

        try:
            response = client_openai.chat.completions.create(
                model=AZURE_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are an expert document validator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )

            result = response.choices[0].message.content.strip()
            print(f"result for checkpoint {checkpoint} is: {result}")

            if "yes" in result.lower():
                validation_results.append(f"✅ Checkpoint '{checkpoint}' fulfilled.")
            else:
                validation_results.append(f"❌ Checkpoint '{checkpoint}' not fulfilled.")

        except Exception as e:
            print(f"Error during validation: {e}")
            validation_results.append(f"⚠️ Error validating checkpoint '{checkpoint}'.")

    return " ".join(validation_results)

@app.route('/')
def index():
    return render_template('checklist.html')

@app.route('/validate', methods=['POST'])
def validate_checklist():
    """Handle file uploads and validate the checklist items."""
    DEBUG_MODE = 0
    uploaded_files = request.files.getlist('fileUpload')
    checklist_data = request.form.get('checklist_data')

    if not checklist_data:
        return jsonify({"error": "Invalid checklist data"}), 400

    checklist_data = json.loads(checklist_data)
    checklist_items = checklist_data['checklist_items']
    validation_results = []

    uploaded_files_info.clear()
    for file in uploaded_files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        uploaded_files_info.append({
            'file_name': file.filename,
            'file_path': file_path,
            'file_url': url_for('static', filename=f'uploads/{file.filename}')
        })

    for item in checklist_items:
        name = item['name'].lower().replace(" ", "")
        checkpoints = item['description']
        # Ensure checkpoints is a list (split by commas if it's a string)
        if isinstance(checkpoints, str):
            checkpoints = [c.strip() for c in checkpoints.split(",") if c.strip()]

        print("row 147, checkpoints=", checkpoints)
        print("row 148, checklist_items=", checklist_items)
        matched_file_found = False
        item_validation_results = []

        for file_info in uploaded_files_info:
            file_name_normalized = file_info['file_name'].lower().replace(" ", "")

            if name in file_name_normalized:
                matched_file_found = True

                if DEBUG_MODE == 0:
                    doc_text = extract_text_from_file(file_info['file_path'])
                    validation_result = validate_document(
                        {"name": name, "checkpoints": checkpoints}, doc_text
                    )
                else:
                    print("use dummy result")
                    validation_result = f"✅ Dummy validation passed for '{name}'"

                item_validation_results.append({
                    'item': name,
                    'document': file_info['file_name'],
                    'file_url': file_info['file_url'],
                    'result': validation_result
                })

        if not matched_file_found:
            item_validation_results.append({
                'item': name,
                'document': 'No matching file found',
                'file_url': '#',
                'result': '❗ No matching file found'
            })

        validation_results.extend(item_validation_results)

    return jsonify(validation_results)

if __name__ == '__main__':
    print("running checklistValidateApp")
    app.run(debug=True, port=5001)
