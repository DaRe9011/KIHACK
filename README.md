# Bürgerservice Wolfsburg – Optimierung durch Automatisierung

## Ziel
Ziel des Projekts ist es, den Bürgerservice in Wolfsburg zu erleichtern, indem automatisierte Prozesse sowohl für Bürger als auch für Beamte bereitgestellt werden. Die Lösung nutzt moderne Technologien wie Chatbots, Azure Document Intelligence und automatisierte Formulare, um den Verwaltungsaufwand zu reduzieren und den Service effizienter zu gestalten.

## Lösungsansatz

### Bürgerseite / Frontend
1. **Chatbot zur Informationsabfrage**
   - Ein Chatbot, der Bürgern ermöglicht, Informationen zu verschiedenen Dienstleistungen direkt von der [Bürgerdienste Wolfsburg-Webseite](https://testwobber.zapier.app/) abzurufen.
   - Der Chatbot bietet eine einfache, interaktive Möglichkeit, Anfragen zu stellen und relevante Informationen schnell zu erhalten.

2. **Online-Formular für Anträge**
   - Ein Formular, das es Bürgern ermöglicht, verschiedene Anträge online zu stellen, einschließlich der Eingabe persönlicher Informationen und dem Hochladen von Dokumenten.
   - Die Flask-basierte Anwendung (`flaskApp.py`) übernimmt die Verwaltung und Verarbeitung der eingereichten Formulare.

### Beamtenseite / Backend
1. **Automatische Dokumentenprüfung mittels Azure**
   - **Azure Document Intelligence** extrahiert den Text aus den hochgeladenen Dokumenten.
   - **Azure OpenAI Service** überprüft, ob alle Checkpoints einer spezifischen Checkliste erfüllt sind.
     - **Mapping der hochgeladenen Dokumente**: Die Dokumente werden automatisch mit der entsprechenden Checkliste (basierend auf dem Namen des Dokuments) abgeglichen.
     - **Checkpunkt-Überprüfung**: Es wird überprüft, ob alle erforderlichen Punkte der Checkliste erfüllt sind.
   - Implementierung in der Datei `checklistValidateApp.py`.

2. **Extraktion und Überprüfung ohne AI-Services**
   - Für spezielle Fälle wird der extrahierte Text aus den Dokumenten manuell überprüft, ohne auf AI-Services zurückzugreifen.
   - Diese Methode wird durch die Skripte `Gui_Dokument_Intelligence.py` und `OCR_Merge.py` ermöglicht.

## Technologien
- **Flask**: Wird für die Bereitstellung der Webanwendung (Formulare) genutzt.
- **Azure Document Intelligence**: Für die Extraktion von Text aus den hochgeladenen Dokumenten.
- **Azure OpenAI Service**: Zur Überprüfung der Dokumente anhand von vordefinierten Checklisten.
- **OCR-Technologie**: Für die Textextraktion aus gescannten Dokumenten.

## Setup und Installation

### Voraussetzungen
- Python 3.x
- Flask
- Azure SDK für Python
- Tesseract (für OCR-basierte Anwendungen)

### Installation

1. **Abhängigkeiten installieren:**

   ```bash
   pip install -r requirements.txt
2. **Azure-Anmeldeinformationen**:

- Stelle sicher, dass du über ein Azure-Konto verfügst und die entsprechenden Anmeldeinformationen für den Zugriff auf Azure Document Intelligence und OpenAI Services hast.
3. **Flask-App starten**:

- Um die Flask-Anwendung zu starten, navigiere in das Verzeichnis, das flaskApp.py enthält, und führe den folgenden Befehl aus:

  ```bash
  python flaskApp.py
4. **Flask-App starten**:

- Um die automatische Dokumentenprüfung zu testen, führe checklistValidateApp.py aus und lade ein Beispiel-Dokument hoch.

  ```bash
  python checklistValidateApp.py
  
## Optimierungen und Erweiterungen
- **Datensicherheit**: Datensicherheit muss sorgfältig beachtet und umgesetzt werden. 
- **Skalierbarkeit**: Um eine bessere Performance bei einer großen Anzahl von Anfragen zu gewährleisten, kann die Anwendung so konzipiert werden, dass sie horizontal skaliert werden kann (z. B. durch den Einsatz von Kubernetes).
- **Dokumenten-Preprocessing**: Dokumenten-Preprocessing: Vor der Extraktion aus gescannten Dokumenten wird eine Preprocessing-Phase empfohlen, um die OCR-Erkennung zu verbessern (z. B. durch Bildverarbeitung).
- **Caching**: Häufige Anfragen (wie Standardchecklisten oder oft abgefragte Informationen) können im Cache gespeichert werden, um die Antwortzeiten zu verkürzen.
