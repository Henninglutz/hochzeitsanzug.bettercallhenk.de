# Kontaktformular - Anti-Spam Implementation

## Übersicht

Das Kontaktformular verfügt über eine **4-stufige Anti-Spam-Schutz**:

### 1. reCAPTCHA v3
- Unsichtbarer Bot-Schutz von Google
- Score-basierte Bewertung (0.0 = Bot, 1.0 = Mensch)
- Threshold: 0.5

### 2. Honeypot-Feld
- Verstecktes "website" Feld
- Nur von Bots ausgefüllt
- Für Menschen unsichtbar

### 3. Zeitstempel-Check
- Bots füllen Formulare zu schnell aus (< 5 Sekunden)
- Menschen brauchen mindestens 5+ Sekunden

### 4. Deutsche Telefon-Validierung
- Nur deutsche Nummern erlaubt: +49, 0049, 0...
- Blockiert internationale Spam-Nummern

## Fake Success für Bots

Wenn ein Bot erkannt wird, erhält er eine **Fake-Success-Response**:
```json
{
  "success": true,
  "message": "Vielen Dank! Wir haben Ihre Anfrage erhalten."
}
```

Der Bot denkt, es hat funktioniert - aber wir speichern/senden nichts!

## Konfiguration

### 1. reCAPTCHA Keys einrichten

Die Keys sind bereits in der Anwendung hinterlegt:
- **Site Key** (öffentlich): `6Ld6h00sAAAAAFtzUGxEg2qj-jY73bYFRcNYjsWt`
- **Secret Key** (privat): Im Code als Fallback

Für Produktion sollte der Secret Key als Umgebungsvariable gesetzt werden:

```bash
export RECAPTCHA_SECRET_KEY=6Ld6h00sAAAAACQzwWStIUqV7pmOfWn3rog6wkD9
```

### 2. Dependencies installieren

```bash
pip install -r requirements.txt
```

Neue Dependency: `requests==2.31.0` (für reCAPTCHA Verifizierung)

### 3. Anwendung starten

```bash
python app.py
```

Oder mit Gunicorn (Produktion):

```bash
gunicorn app:app
```

## Formular-Features

### Frontend (templates/hochzeitsanzug.html)
- ✅ Kontaktformular mit allen Pflichtfeldern
- ✅ Honeypot-Feld (versteckt)
- ✅ Zeitstempel-Feld (versteckt)
- ✅ reCAPTCHA v3 Script

### JavaScript (static/hochzeitsanzug.js)
- ✅ Deutsche Telefon-Validierung
- ✅ Client-seitige Validierung
- ✅ reCAPTCHA Token-Generierung
- ✅ AJAX Submit mit Fetch API
- ✅ Error Handling & Success Messages

### Backend (app.py)
- ✅ POST /api/contact Endpoint
- ✅ reCAPTCHA v3 Verifizierung mit Google
- ✅ Honeypot-Check
- ✅ Zeitstempel-Check (< 5 Sek = Bot)
- ✅ Deutsche Telefon-Validierung (Regex)
- ✅ Fake-Success für Bots
- ✅ Email-Versand (Placeholder)

## Email-Versand implementieren

Der Email-Versand ist aktuell ein **Placeholder**. Für Produktion sollten Sie einen echten Email-Service implementieren:

### Option 1: SMTP (Gmail, Office365, etc.)

```python
import smtplib
from email.mime.text import MIMEText

def send_contact_email(name, email, phone, wedding_date, message):
    msg = MIMEText(f"""
    Neue Kontaktanfrage:
    
    Name: {name}
    Email: {email}
    Telefon: {phone}
    Hochzeitstermin: {wedding_date}
    Nachricht: {message}
    """)
    
    msg['Subject'] = f'Neue Anfrage von {name}'
    msg['From'] = 'noreply@bettercallhenk.de'
    msg['To'] = 'henk@bettercallhenk.de'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@gmail.com', 'your-app-password')
        server.send_message(msg)
    
    return True
```

### Option 2: SendGrid API

```python
import sendgrid
from sendgrid.helpers.mail import Mail

def send_contact_email(name, email, phone, wedding_date, message):
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    
    mail = Mail(
        from_email='noreply@bettercallhenk.de',
        to_emails='henk@bettercallhenk.de',
        subject=f'Neue Anfrage von {name}',
        html_content=f'<p>Name: {name}</p>...'
    )
    
    response = sg.send(mail)
    return response.status_code == 202
```

## Logging & Monitoring

Die App loggt alle Bot-Erkennungen:

```
🤖 BOT DETECTED (Honeypot): spam@example.com
🤖 BOT DETECTED (Too Fast): bot@example.com - 1.23s
🤖 BOT DETECTED (Low Score): suspicious@example.com - Score: 0.3
✅ REAL USER: real@example.com - reCAPTCHA Score: 0.9
📧 Email sent successfully to henk@bettercallhenk.de
```

Überwachen Sie die Logs um zu sehen wie effektiv der Anti-Spam-Schutz arbeitet.

## Testing

### Test 1: Echte Submission (sollte funktionieren)
1. Öffnen Sie die Seite
2. Warten Sie 5+ Sekunden
3. Füllen Sie alle Felder korrekt aus
4. Deutsche Telefonnummer verwenden: `0160 1234567`
5. Submit → Sollte erfolgreich sein

### Test 2: Bot-Simulation (sollte Fake-Success geben)
1. Honeypot füllen: DevTools → Feld "website" ausfüllen
2. Submit → Fake Success
3. Oder: Submit in < 5 Sekunden → Fake Success

### Test 3: Internationale Nummer (sollte fehlschlagen)
1. Nummer eingeben: `+1 555 123 4567` (USA)
2. Submit → Error: "Bitte geben Sie eine gültige deutsche Telefonnummer ein."

## Anpassungen

### Zeitstempel-Schwelle ändern

In `app.py`:

```python
MIN_FORM_SUBMIT_TIME = 5  # Auf 10 erhöhen für strengeren Check
```

### reCAPTCHA Score-Schwelle ändern

In `app.py`:

```python
RECAPTCHA_SCORE_THRESHOLD = 0.5  # Auf 0.7 erhöhen für strengeren Check
```

Höherer Wert = weniger Bots durchkommen, aber auch Risiko false positives

## Support

Bei Fragen oder Problemen:
- Email: henk@bettercallhenk.de
- Tel: +49 160 7857633

---

**Status**: ✅ Implementiert und einsatzbereit
**Dependencies**: Flask, Flask-CORS, requests
**Python Version**: 3.11+
