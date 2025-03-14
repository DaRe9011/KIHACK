from flask import Flask, render_template_string, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from OCR_Merge import *
import json


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a random string in production

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Define the document types
# DOCUMENT_TYPES = {
#     'ausweisdokument': 'Ausweisdokument',
#     'wohnbestaetigung': 'Wohnbestätigung',
#     'formular': 'Formular'
# }

DOCUMENT_TYPES = {
    'ausweisdokument': 'Ausweisdokument',
    'wohnbestaetigung': 'Wohnbestätigung',
    'formular': 'Formular'
}

# HTML template as a string
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Document Selection</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: #f9f9f9;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .document-row {
            margin-bottom: 15px;
            padding: 15px;
            background-color: #fff;
            border-radius: 5px;
            border: 1px solid #ddd;
            display: flex;
            align-items: center;
        }
        .document-row.selected {
            background-color: #e9ffe9;
        }
        .document-name {
            font-weight: bold;
            width: 180px;
            flex-shrink: 0;
        }
        .file-selection {
            display: flex;
            flex-grow: 1;
            align-items: center;
        }
        .selected-file {
            margin-right: 15px;
            font-style: italic;
            color: #0a5;
        }
        button, input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            padding: 8px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover, input[type="submit"]:hover {
            background-color: #45a049;
        }
        .process-btn {
            background-color: #2196F3;
            margin-top: 20px;
            padding: 12px 20px;
            font-weight: bold;
            font-size: 16px;
        }
        .process-btn:hover {
            background-color: #0b7dda;
        }
        .reset-btn {
            background-color: #f44336;
            margin-left: 10px;
        }
        .reset-btn:hover {
            background-color: #d32f2f;
        }
        input[type="file"] {
            padding: 5px;
            margin-right: 10px;
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        .buttons-container {
            margin-top: 20px;
            display: flex;
            align-items: center;
        }
    </style>

</head>
<body>
    <div class="container">
        <h1>Document Selection</h1>
        <p>Please select the required documents:</p>

        {% for doc_key, doc_name in document_types.items() %}
            <div class="document-row">
                <div class="document-name">{{ doc_name }}:</div>
                <div class="file-selection">
                    <form method="post" enctype="multipart/form-data">
                        <input type="hidden" name="doc_type" value="{{ doc_key }}">
                        <input type="file" name="{{ doc_key }}" multiple id="{{ doc_key }}">
                        <input type="submit" value="Upload">
                    </form>
                    <div class="file-list">
                        {% if doc_key in selected_docs %}
                            {% for file in selected_docs[doc_key] %}
                                <div class="file-item">
                                    <span>{{ file['filename'] }}</span>
                                    <span class="remove-file" onclick="removeFile('{{ doc_key }}', '{{ file['filename'] }}')">Remove</span>
                                </div>
                            {% endfor %}
                        {% endif %}
                    </div>
                </div>
            </div>
        {% endfor %}

        <div class="buttons-container">
            <form method="post" action="{{ url_for('process_documents') }}">
                <input type="submit" value="Process Documents" class="process-btn">
            </form>

            <form method="post" style="margin-left: 10px;">
                <input type="hidden" name="reset" value="true">
                <input type="submit" value="Reset" class="reset-btn">
            </form>
        </div>
    </div>

    <script>
        function removeFile(docType, filename) {
            fetch('/remove_file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({doc_type: docType, filename: filename}),
            }).then(() => {
                location.reload();
            });
        }
    </script>
</body>
</html>
'''

RESULT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Processing Results</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: #fff;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Processing Results</h1>
        <table>
            <tr>
                <th>Field</th>
                <th>Value</th>
            </tr>
            {% for key, value in result.items() %}
            <tr>
                <td>{{ key.replace('_', ' ').title() }}</td>
                <td>{{ value }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Clear previous selections if starting over
        if 'reset' in request.form:
            session.clear()
            return redirect(url_for('index'))

        # Handle file upload
        doc_type = request.form.get('doc_type')
        if doc_type and doc_type in DOCUMENT_TYPES:
            files = request.files.getlist(doc_type)
            for file in files:
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    # Store the document information in session
                    if 'documents' not in session:
                        session['documents'] = {}
                    if doc_type not in session['documents']:
                        session['documents'][doc_type] = []

                    session['documents'][doc_type].append({
                        'filename': filename,
                        'path': filepath
                    })
                    session.modified = True

            return redirect(url_for('index'))

    # Get currently selected documents
    selected_docs = session.get('documents', {})
    return render_template_string(HTML_TEMPLATE, selected_docs=selected_docs, document_types=DOCUMENT_TYPES)


@app.route('/remove_file', methods=['POST'])
def remove_file():
    data = request.json
    doc_type = data.get('doc_type')
    filename = data.get('filename')

    if 'documents' in session and doc_type in session['documents']:
        session['documents'][doc_type] = [doc for doc in session['documents'][doc_type] if doc['filename'] != filename]
        session.modified = True

        # Remove the file from the upload folder
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    return '', 204


@app.route('/process', methods=['POST'])
def process_documents():
    # Get the selected documents from the session
    selected_docs = session.get('documents', {})

    # Print the contents of selected_docs
    print("Contents of selected_docs:")
    print(selected_docs)

    reduced_result = {}
    for doc_type, files in selected_docs.items():
        if doc_type == 'ausweisdokument':
            with open('structure_id.json') as f:
                structure_template = json.load(f)
            documents = [file['path'] for file in selected_docs['ausweisdokument']]

            reduced_result = document_analyzer(documents, structure_template)

    # reduced_result is already a dictionary, so we can use it directly
    return render_template_string(RESULT_TEMPLATE, result=reduced_result)


if __name__ == '__main__':
    app.run(debug=True)