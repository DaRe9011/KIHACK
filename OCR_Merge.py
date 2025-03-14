from azure.core.credentials import AzureKeyCredential
#from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.ai.documentintelligence.models import DocumentAnalysisFeature
import base64
import os
import json

endpoint = "<INSERT-YOUR-ENDPOINT>"
key = "<INSERT-YOUR-KEY>"

def analyze_document(file_path):
    document_intelligence_client  = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    # Lokaler Dateipfad
    #local_file_path = "AusweisErikaMustermannVorderseite.jpg"

    # Öffnen und lesen Sie die Datei
    with open(file_path, "rb") as document_file:
        document_content = base64.b64encode(document_file.read()).decode()

    query_fields = ["Name", "Geburtsname", "Vorname", "Geburtstag", "Staatsangehoerigkeit", "Geburtsort", "Geschlecht",
                    "Unterschrift", "Photo", "Gueltig_bis", "Authority"]
    # Erstellen Sie ein AnalyzeDocumentRequest-Objekt
    request = AnalyzeDocumentRequest(bytes_source=document_content)

    # Starten Sie die Analyse
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-idDocument",
        body=request, features=[DocumentAnalysisFeature.QUERY_FIELDS], query_fields=query_fields  # Verwenden Sie 'body' als Argument-Name
    )
    return poller.result()

def get_id_document(document, id_card_document):
    #id_card_document = structure_template
    for field, content in document["fields"].items():
        if field in ["DateOfBirth", "Geburtstag"] and id_card_document["personal_info"]["birth_date"] is None:
            try:
                id_card_document["personal_info"]["birth_date"] = content["content"]
            except:
                pass
        elif field in ["DateOfExpiration", "Gültig_bis"] and id_card_document["id_card"]["valid_until"] is None:
            try:
                id_card_document["id_card"]["valid_until"] = content["content"]
            except:
                pass
        elif field in ["DocumentDiscriminator"] and id_card_document["id_card"]["card_access_number"] is None:
            try:
                id_card_document["id_card"]["card_access_number"] = content["content"]
            except:
                pass
        elif field in ["DocumentNumber"] and id_card_document["id_card"]["document_number"] is None:
            try:
                id_card_document["id_card"]["document_number"]  = content["content"]
            except:
                pass
        elif field in ["FirstName", "Vorname"] and id_card_document["personal_info"]["name"] is None:
            try:
                id_card_document["personal_info"]["name"]  = content["content"]
            except:
                pass
        elif field in ["LastName", "Name"] and id_card_document["personal_info"]["surname"] is None:
            try:
                id_card_document["personal_info"]["surname"]  = content["content"]
            except:
                pass
        elif field in ["PlaceOfBirth", "Geburtsort"] and id_card_document["personal_info"]["birth_place"] is None:
            try:
                id_card_document["personal_info"]["birth_place"]  = content["content"]
            except:
                pass
        elif field in ["Geburtsname"] and id_card_document["personal_info"]["former_surname"] is None:
            try:
                id_card_document["personal_info"]["former_surname"]  = content["content"]
            except:
                pass
        elif field in ["Geschlecht", "Sex"] and id_card_document["personal_info"]["sex"] is None:
            try:
                id_card_document["personal_info"]["sex"]  = content["content"]
            except:
                pass
        elif field in ["Nationality", "Staatsangehörigkeit", "Staatsangehoerigkeit"] and id_card_document["personal_info"]["nationality"] is None:
            try:
                id_card_document["personal_info"]["nationality"]  = content["content"]
            except:
                pass
        elif field in ["Address"]:
            '''
            try:
                id_card_document["personal_info"]["nationality"]  = content["content"]
            except:
                pass
            '''
            try:
                res = content["content"]
                contents = res.replace("\n", " ").split(" ")
                id_card_document["current_address"]["zip_code"]  = contents[0]
                id_card_document["current_address"]["city"]  = contents[1]
                id_card_document["current_address"]["street"]  = contents[2]
                id_card_document["current_address"]["house_number"]  = contents[3]
            except:
                pass
        elif field in ["DateOfIssue"] and id_card_document["id_card"]["date"] is None:
            try:
                id_card_document["id_card"]["date"]  = content["content"]
            except:
                pass
        # elif field in ["Ausstellbehoerde", "Authority"] and id_card_document["id_card"]["authority"] is None:
        #     try:
        #         id_card_document["id_card"]["authority"]  = content["content"]
        #     except:
        #         pass
        elif field in ["EyeColor"] and id_card_document["general_id_info"]["eye_colour"] is None:
            try:
                id_card_document["general_id_info"]["eye_colour"]  = content["content"]
            except:
                pass
        elif field in ["Height"] and id_card_document["general_id_info"]["height"] is None:
            try:
                id_card_document["general_id_info"]["height"]  = content["content"]
            except:
                pass
        elif field in ["Height"] and id_card_document["general_id_info"]["height"] is None:
            try:
                id_card_document["general_id_info"]["height"]  = content["content"]
            except:
                pass
        else:
            try:
                print(field)
                print(content["content"])
            except:
                pass

    with open("all_id_card_document.json", "w", encoding="utf-8") as f:
        json.dump(id_card_document, f, indent=4)

    return id_card_document


def analyze_id_document(id_document):
    # prepare local info
    local_dict = {"name": id_document["personal_info"]["name"],
                  "surname": id_document["personal_info"]["surname"],
                  "former_surname": id_document["personal_info"]["former_surname"],
                  "birth_date": id_document["personal_info"]["birth_date"],
                  "birth_place": id_document["personal_info"]["birth_place"],
                  "nationality": id_document["personal_info"]["nationality"],
                  "document_number": id_document["id_card"]["document_number"],
                  "card_access_number": id_document["id_card"]["card_access_number"],
                  "date": id_document["id_card"]["date"],
                  "expiration_date": id_document["id_card"]["valid_until"],
                  "eye_colour": id_document["general_id_info"]["eye_colour"],
                  "height": id_document["general_id_info"]["height"],
                  "zip_code": id_document["current_address"]["zip_code"],
                  "city": id_document["current_address"]["city"],
                  "street": id_document["current_address"]["street"],
                  "house_number": id_document["current_address"]["house_number"]
                  }

    create_txt_report(local_dict=local_dict, file_name="id_document_report.txt")

    # with open("reduced_id_card_document.json", "w") as outfile:
    # json.dump(local_dict, f, indent=4)

    with open("reduced_id_card_document.json", "w", encoding="utf-8") as f:
        json.dump(local_dict, f, indent=4)

    return local_dict

def analyze_result(result_jsons, structure_template):
    id_card_document = structure_template
    for result_json in result_jsons:
        #with open(result_json) as f:
            #result = json.load(f)
            for document in result_json["documents"]:
                if document["docType"] == 'idDocument.nationalIdentityCard':
                    id_card_document = get_id_document(document=document, id_card_document=id_card_document)
    local_dict =analyze_id_document(id_document=id_card_document)
    return local_dict

def create_txt_report(local_dict, file_name):
    found_data = []
    missing_data = []
    
    for key, value in local_dict.items():
        if value is not None:
            strg = "%s: %s" % (key, value)
            found_data.append(strg)
        else:
            missing_data.append(key)

    # open file
    with open(file_name, 'w') as f:
        
        f.write("Found elements:")
        for items in found_data:
            f.write('\n%s' %items)
        
        f.write("\n")

        f.write("\nMissing elements:")
        for items in missing_data:
            f.write('\n%s' %items)
        
        print("File written successfully")


    # close the file
    f.close()
def document_analyzer(documents, structure_template):
    dict_list = []
    for doc in documents:
        dict_list.append(analyze_document(doc))
    reduced_result = analyze_result(result_jsons=dict_list, structure_template=structure_template)
    return reduced_result


if __name__ == "__main__":

    try:
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    except:
        os.chdir(os.getcwd())

    with open('structure_id.json') as f:
        structure_template = json.load(f)

    documents = ["AusweisErikaMustermannRückseite.jpg", "AusweisErikaMustermannVorderseite.jpg"]

    results = document_analyzer(documents, structure_template)

    print(results)