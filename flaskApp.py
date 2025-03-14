from flask import Flask, render_template, request, redirect, session, jsonify
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed to store session data

# Language Translations (English & German)
translations = {
    "en": {
        "title": "Government Public Services",
        "description": "Welcome to our government service portal.",
        "residence_registeration": "Residence Registeration",
        "residence_registeration_desc": "registerate your resident in Wolfsburg",
        "start_now": "Start Now",
        "home": "Home",
        "upload_title": "Please fill the form and upload your documents",
        "name": "Name",
        "email": "Email",
        "upload_files": "Upload Files",
        "submit": "Submit"
    },
    "de": {
        "title": "Öffentliche Regierungsdienste",
        "description": "Willkommen auf unserem Regierungsdienst-Portal.",
        "residence_registeration": "Anmeldung des Wohnsitzes",
        "residence_registeration_desc": "Anmeldung des Wohnsitzes in Wolfsburg",
        "start_now": "Jetzt starten",
        "home": "Startseite",
        "upload_title": "Füllen Sie das Formular aus und laden Sie Ihre Dokumente hoch",
        "name": "Name",
        "email": "E-Mail",
        "upload_files": "Dateien hochladen",
        "submit": "Einreichen"
    }
}

# Route to set language
@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in translations:
        session['lang'] = lang
    return redirect(request.referrer or '/')

@app.route('/')
def home():
    lang = session.get('lang', 'en')  # Default to English
    return render_template('index.html', translations=translations[lang], lang=lang)

@app.route('/form', methods=['GET', 'POST'])
def form():
    lang = session.get('lang', 'en')
    return render_template('form.html', translations=translations[lang], lang=lang)

if __name__ == "__main__":
    app.run(debug=True)
