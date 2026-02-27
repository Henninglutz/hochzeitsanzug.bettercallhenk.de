"""
Hochzeitsanzug Landing Page - Standalone Flask Application
Optimized for deployment at hochzeitsanzug.bettercallhenk.de
"""

import os
import re
import time
import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS Configuration
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# reCAPTCHA Configuration
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', '6Ld6h00sAAAAACQzwWStIUqV7pmOfWn3rog6wkD9')
RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

# Anti-Spam Configuration
MIN_FORM_SUBMIT_TIME = 5  # seconds - Bots submit faster than 5 seconds
RECAPTCHA_SCORE_THRESHOLD = 0.5  # reCAPTCHA v3 score threshold (0.0 = bot, 1.0 = human)

# Pipedrive API Configuration
PIPEDRIVE_API_TOKEN = os.environ.get('PIPEDRIVE_API_TOKEN', '')
PIPEDRIVE_COMPANY_DOMAIN = os.environ.get('PIPEDRIVE_COMPANY_DOMAIN', '')
PIPEDRIVE_API_BASE = f'https://{PIPEDRIVE_COMPANY_DOMAIN}.pipedrive.com/api/v1' if PIPEDRIVE_COMPANY_DOMAIN else ''
PIPEDRIVE_PIPELINE_NAME = os.environ.get('PIPEDRIVE_PIPELINE_NAME', 'BETTERCALLHENK')
PIPEDRIVE_STAGE_NAME = os.environ.get('PIPEDRIVE_STAGE_NAME', 'Teaser henk')
PIPEDRIVE_FIELD_WEDDING_DATE = '5d0c64df2a706315462ca7d758971d9711d65de2'
PIPEDRIVE_FIELD_WHATSAPP_CONSENT = '10ad5ed0620f139d337e46186c1fd043986b998d'

# Email Notification Configuration
SMTP_HOST = os.environ.get('SMTP_HOST', '')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@bettercallhenk.de')
NOTIFICATION_EMAILS = os.environ.get('NOTIFICATION_EMAILS', 'henk@bettercallhenk.de,henning@bettercallhenk.de')

# Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
    strategy="fixed-window",
)


@app.route('/')
def index():
    """
    Serve the Hochzeitsanzug (Wedding Suit) landing page.

    This is a high-converting landing page optimized for:
    - Human grooms looking for wedding suits
    - AI/LLM search engines (GEO - Generative Engine Optimization)
    - SEO with structured data (JSON-LD for ClothingStore and FAQPage)

    Returns:
        Rendered HTML template with full SEO meta tags and structured data
    """
    return render_template('hochzeitsanzug.html')


@app.route('/kraft-boxer')
def kraft_boxer():
    """Serve the Kraft Boxer landing page for athletic tailoring."""
    return render_template('kraft-boxer.html')


@app.route('/danke')
def thank_you():
    """Serve the thank you page after a successful booking."""
    return render_template('danke.html')


@app.route('/api/contact', methods=['POST'])
@limiter.limit("5 per minute")
@limiter.limit("20 per hour")
@limiter.limit("50 per day")
def contact_form():
    """
    Contact Form Submission with Multi-Layer Anti-Spam Protection

    Anti-Spam Layers:
    1. reCAPTCHA v3 verification (score >= 0.5)
    2. Honeypot field check (website field must be empty)
    3. Timestamp check (submission must be >= 5 seconds after page load)
    4. German phone validation (only +49 / 0... numbers)

    Bots get fake success response (so they think it worked)
    Real users get email notification
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'message': 'Keine Daten erhalten'}), 400

        # Extract form data
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        wedding_date = data.get('wedding_date', '').strip()
        message = data.get('message', '').strip()
        honeypot = data.get('website', '').strip()
        form_loaded_at = data.get('form_loaded_at', '0')
        recaptcha_token = data.get('recaptcha_token', '')
        source_page = data.get('source', 'unknown').strip()
        whatsapp_consent = data.get('whatsapp_consent', False)

        # === ANTI-SPAM CHECK 1: Honeypot Field ===
        if honeypot:
            logger.warning(f'🤖 BOT DETECTED (Honeypot): {email}')
            # Fake success for bots
            return jsonify({
                'success': True,
                'message': 'Vielen Dank! Wir haben Ihre Anfrage erhalten.'
            }), 200

        # === ANTI-SPAM CHECK 2: Timestamp Check (< 5 sec = bot) ===
        try:
            form_load_time = int(form_loaded_at) / 1000  # Convert ms to seconds
            current_time = time.time()
            time_elapsed = current_time - form_load_time

            if time_elapsed < MIN_FORM_SUBMIT_TIME:
                logger.warning(f'🤖 BOT DETECTED (Too Fast): {email} - {time_elapsed:.2f}s')
                # Fake success for bots
                return jsonify({
                    'success': True,
                    'message': 'Vielen Dank! Wir haben Ihre Anfrage erhalten.'
                }), 200
        except (ValueError, TypeError):
            logger.warning(f'🤖 BOT DETECTED (Invalid Timestamp): {email}')
            return jsonify({
                'success': True,
                'message': 'Vielen Dank! Wir haben Ihre Anfrage erhalten.'
            }), 200

        # === ANTI-SPAM CHECK 3: reCAPTCHA v3 Verification ===
        if recaptcha_token:
            recaptcha_score = verify_recaptcha(recaptcha_token, request.remote_addr)

            if recaptcha_score is None:
                logger.warning(f'🤖 BOT DETECTED (reCAPTCHA Failed): {email}')
                return jsonify({
                    'success': True,
                    'message': 'Vielen Dank! Wir haben Ihre Anfrage erhalten.'
                }), 200

            if recaptcha_score < RECAPTCHA_SCORE_THRESHOLD:
                logger.warning(f'🤖 BOT DETECTED (Low Score): {email} - Score: {recaptcha_score}')
                return jsonify({
                    'success': True,
                    'message': 'Vielen Dank! Wir haben Ihre Anfrage erhalten.'
                }), 200
        else:
            # No token - reCAPTCHA likely blocked by adblocker
            # Other 3 checks (honeypot, timestamp, phone) still protect us
            logger.info(f'reCAPTCHA skipped (likely adblocker) for: {email}')
            recaptcha_score = None

        # === ANTI-SPAM CHECK 4: German Phone Validation ===
        if not validate_german_phone(phone):
            logger.warning(f'❌ Invalid German Phone: {email} - {phone}')
            return jsonify({
                'success': False,
                'message': 'Bitte geben Sie eine gültige deutsche Telefonnummer ein.'
            }), 400

        # === VALIDATION: Required Fields ===
        if not all([name, email, phone, message]):
            return jsonify({
                'success': False,
                'message': 'Bitte füllen Sie alle Pflichtfelder aus.'
            }), 400

        if not whatsapp_consent:
            return jsonify({
                'success': False,
                'message': 'Bitte stimmen Sie der WhatsApp-Kontaktaufnahme zu.'
            }), 400

        # === ALL CHECKS PASSED - Real Human User ===
        logger.info(f'✅ REAL USER: {email} - reCAPTCHA Score: {recaptcha_score} - Source: {source_page}')

        # Create lead in Pipedrive CRM
        lead_created = create_pipedrive_lead(name, email, phone, wedding_date, message, source_page, whatsapp_consent)

        if lead_created:
            logger.info(f'📧 Lead created in Pipedrive for {email}')
            return jsonify({
                'success': True,
                'message': 'Vielen Dank! Wir haben Ihre Anfrage erhalten und melden uns bald bei Ihnen.'
            }), 200
        else:
            logger.error(f'❌ Lead creation failed for {email}')
            return jsonify({
                'success': False,
                'message': 'Es gab ein Problem beim Versenden. Bitte versuchen Sie es erneut oder rufen Sie uns direkt an.'
            }), 500

    except Exception as e:
        logger.error(f'❌ Contact form error: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.'
        }), 500


def verify_recaptcha(token, remote_ip):
    """
    Verify reCAPTCHA v3 token with Google

    Returns:
        float: Score between 0.0 (bot) and 1.0 (human)
        None: If verification failed
    """
    if not token:
        return None

    try:
        response = requests.post(
            RECAPTCHA_VERIFY_URL,
            data={
                'secret': RECAPTCHA_SECRET_KEY,
                'response': token,
                'remoteip': remote_ip
            },
            timeout=5
        )

        result = response.json()

        if result.get('success'):
            score = result.get('score', 0.0)
            logger.info(f'reCAPTCHA verified - Score: {score}')
            return score
        else:
            error_codes = result.get('error-codes', [])
            logger.warning(f'reCAPTCHA verification failed: {error_codes}')
            return None

    except Exception as e:
        logger.error(f'reCAPTCHA verification error: {str(e)}')
        return None


def validate_german_phone(phone):
    """
    Validate German phone number

    Accepts:
    - +49 followed by 9-15 digits
    - 0049 followed by 9-15 digits
    - 0 followed by 9-15 digits (German local format)

    Rejects:
    - International numbers (not starting with +49/0049/0)
    - Invalid formats
    """
    if not phone:
        return False

    # Remove spaces and common separators
    phone_clean = re.sub(r'[\s\-\(\)\/]', '', phone)

    # German phone regex
    # Matches: +49..., 0049..., 0...
    german_phone_pattern = r'^(\+49|0049|0)[1-9]\d{1,14}$'

    return bool(re.match(german_phone_pattern, phone_clean))


def send_lead_email(name, email, phone, wedding_date, message, source_page, whatsapp_consent, is_fallback=False):
    """
    Send lead notification email to internal team (Henk & Henning)
    and a confirmation email to the customer.
    """
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        logger.warning('SMTP not configured - skipping email notification (set SMTP_HOST, SMTP_USER, SMTP_PASSWORD)')
        return False

    recipients = [r.strip() for r in NOTIFICATION_EMAILS.split(',') if r.strip()]
    if not recipients:
        logger.warning('No NOTIFICATION_EMAILS configured - skipping email')
        return False

    subject_prefix = '[PIPEDRIVE FEHLER - DIREKT REAGIEREN]' if is_fallback else '[Neue Anfrage]'
    subject = f'{subject_prefix} Hochzeitsanzug-Anfrage von {name}'

    html_body = f"""
    <html><body>
    <h2>{'⚠️ PIPEDRIVE NICHT ERREICHBAR - Bitte Lead manuell anlegen!' if is_fallback else '✅ Neue Kontaktanfrage'}</h2>
    <table style="border-collapse:collapse;width:100%">
      <tr><td style="padding:8px;font-weight:bold;background:#f5f5f5">Seite</td><td style="padding:8px">{source_page}</td></tr>
      <tr><td style="padding:8px;font-weight:bold;background:#f5f5f5">Name</td><td style="padding:8px">{name}</td></tr>
      <tr><td style="padding:8px;font-weight:bold;background:#f5f5f5">Email</td><td style="padding:8px"><a href="mailto:{email}">{email}</a></td></tr>
      <tr><td style="padding:8px;font-weight:bold;background:#f5f5f5">Telefon</td><td style="padding:8px"><a href="tel:{phone}">{phone}</a></td></tr>
      <tr><td style="padding:8px;font-weight:bold;background:#f5f5f5">Hochzeitstermin</td><td style="padding:8px">{wedding_date or 'Nicht angegeben'}</td></tr>
      <tr><td style="padding:8px;font-weight:bold;background:#f5f5f5">WhatsApp-Zustimmung</td><td style="padding:8px">{'✅ Ja' if whatsapp_consent else '❌ Nein'}</td></tr>
      <tr><td style="padding:8px;font-weight:bold;background:#f5f5f5">Nachricht</td><td style="padding:8px">{message}</td></tr>
    </table>
    </body></html>
    """

    text_body = (
        f"{'PIPEDRIVE FEHLER - Bitte Lead manuell anlegen!' if is_fallback else 'Neue Kontaktanfrage'}\n\n"
        f"Seite: {source_page}\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Telefon: {phone}\n"
        f"Hochzeitstermin: {wedding_date or 'Nicht angegeben'}\n"
        f"WhatsApp-Zustimmung: {'Ja' if whatsapp_consent else 'Nein'}\n"
        f"Nachricht:\n{message}\n"
    )

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = ', '.join(recipients)
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, recipients, msg.as_string())

        logger.info(f'Lead notification email sent to {recipients} for {email}')
    except Exception as e:
        logger.error(f'Failed to send lead notification email: {str(e)}')
        return False

    # Send confirmation email to customer
    try:
        confirm_msg = MIMEMultipart('alternative')
        confirm_msg['Subject'] = 'Ihre Anfrage bei bettercallhenk - Hochzeitsanzug'
        confirm_msg['From'] = FROM_EMAIL
        confirm_msg['To'] = email

        confirm_html = f"""
        <html><body>
        <h2>Vielen Dank für Ihre Anfrage, {name}!</h2>
        <p>Wir haben Ihre Nachricht erhalten und melden uns so schnell wie möglich bei Ihnen.</p>
        <p>Bei dringenden Fragen erreichen Sie uns direkt:</p>
        <ul>
          <li>📱 WhatsApp / Telefon: <a href="tel:+4916078576333">+49 160 78 57 633</a></li>
          <li>📧 Email: <a href="mailto:henk@bettercallhenk.de">henk@bettercallhenk.de</a></li>
        </ul>
        <p><b>Ihre Anfrage im Überblick:</b></p>
        <table style="border-collapse:collapse">
          <tr><td style="padding:4px 12px 4px 0;font-weight:bold">Hochzeitstermin:</td><td>{wedding_date or 'Noch nicht festgelegt'}</td></tr>
          <tr><td style="padding:4px 12px 4px 0;font-weight:bold">Nachricht:</td><td>{message}</td></tr>
        </table>
        <br>
        <p>Mit freundlichen Grüßen,<br><b>Henk – bettercallhenk</b></p>
        </body></html>
        """

        confirm_text = (
            f"Vielen Dank für Ihre Anfrage, {name}!\n\n"
            f"Wir haben Ihre Nachricht erhalten und melden uns so schnell wie möglich bei Ihnen.\n\n"
            f"Bei dringenden Fragen: +49 160 78 57 633 oder henk@bettercallhenk.de\n\n"
            f"Hochzeitstermin: {wedding_date or 'Noch nicht festgelegt'}\n"
            f"Nachricht: {message}\n\n"
            f"Mit freundlichen Grüßen,\nHenk – bettercallhenk"
        )

        confirm_msg.attach(MIMEText(confirm_text, 'plain', 'utf-8'))
        confirm_msg.attach(MIMEText(confirm_html, 'html', 'utf-8'))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, [email], confirm_msg.as_string())

        logger.info(f'Confirmation email sent to customer {email}')
    except Exception as e:
        logger.error(f'Failed to send customer confirmation email: {str(e)}')
        # Non-critical: team notification was already sent, don't fail

    return True


def _find_stage_id(pipeline_name, stage_name):
    """Resolve Pipedrive stage ID by pipeline and stage name."""
    try:
        pipelines_response = requests.get(
            f'{PIPEDRIVE_API_BASE}/pipelines?api_token={PIPEDRIVE_API_TOKEN}',
            timeout=10
        )
        pipelines_result = pipelines_response.json()

        if not pipelines_result.get('success'):
            logger.warning(f'Could not load Pipedrive pipelines: {pipelines_result}')
            return None

        pipeline_id = next(
            (
                item.get('id') for item in pipelines_result.get('data', [])
                if item.get('name', '').strip().lower() == pipeline_name.strip().lower()
            ),
            None
        )

        if not pipeline_id:
            logger.warning(f'Pipeline not found in Pipedrive: {pipeline_name}')
            return None

        stages_response = requests.get(
            f'{PIPEDRIVE_API_BASE}/stages?api_token={PIPEDRIVE_API_TOKEN}&pipeline_id={pipeline_id}',
            timeout=10
        )
        stages_result = stages_response.json()

        if not stages_result.get('success'):
            logger.warning(f'Could not load Pipedrive stages: {stages_result}')
            return None

        stage_id = next(
            (
                item.get('id') for item in stages_result.get('data', [])
                if item.get('name', '').strip().lower() == stage_name.strip().lower()
            ),
            None
        )

        if not stage_id:
            logger.warning(f'Stage not found in Pipedrive pipeline {pipeline_name}: {stage_name}')

        return stage_id

    except Exception as e:
        logger.warning(f'Could not resolve stage id for pipeline/stage names: {str(e)}')
        return None


def create_pipedrive_lead(name, email, phone, wedding_date, message, source_page='unknown', whatsapp_consent=False):
    """
    Create a Person and Deal in Pipedrive CRM.
    Falls back to logging if Pipedrive is not configured or unavailable.
    """
    if not PIPEDRIVE_API_TOKEN or not PIPEDRIVE_API_BASE:
        logger.error('Pipedrive API not configured - missing PIPEDRIVE_API_TOKEN or PIPEDRIVE_COMPANY_DOMAIN')
        _log_lead_fallback(name, email, phone, wedding_date, message, source_page, whatsapp_consent)
        return True

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    try:
        # Step 1: Create Person
        person_data = {
            'name': name,
            'email': [{'value': email, 'primary': True}],
            'phone': [{'value': phone, 'primary': True}],
        }

        person_response = requests.post(
            f'{PIPEDRIVE_API_BASE}/persons?api_token={PIPEDRIVE_API_TOKEN}',
            json=person_data,
            headers=headers,
            timeout=10
        )

        person_result = person_response.json()

        if not person_result.get('success'):
            logger.error(f'Pipedrive person creation failed: {person_result}')
            _log_lead_fallback(name, email, phone, wedding_date, message, source_page, whatsapp_consent)
            return True

        person_id = person_result['data']['id']
        logger.info(f'Pipedrive person created: ID {person_id} for {email}')

        # Step 2: Create Deal linked to Person in configured pipeline/stage
        deal_title = f'LP {source_page.replace("-", " ").title()} - {name}'
        stage_id = _find_stage_id(PIPEDRIVE_PIPELINE_NAME, PIPEDRIVE_STAGE_NAME)

        deal_data = {
            'title': deal_title,
            'person_id': person_id,
            'status': 'open',
            PIPEDRIVE_FIELD_WEDDING_DATE: wedding_date or None,
            PIPEDRIVE_FIELD_WHATSAPP_CONSENT: 'accepted' if whatsapp_consent else None,
        }

        if stage_id:
            deal_data['stage_id'] = stage_id

        deal_response = requests.post(
            f'{PIPEDRIVE_API_BASE}/deals?api_token={PIPEDRIVE_API_TOKEN}',
            json=deal_data,
            headers=headers,
            timeout=10
        )

        deal_result = deal_response.json()

        if not deal_result.get('success'):
            logger.error(f'Pipedrive deal creation failed: {deal_result}')
            _log_lead_fallback(name, email, phone, wedding_date, message, source_page, whatsapp_consent)
            return True

        deal_id = deal_result['data']['id']
        logger.info(
            f'Pipedrive deal created: ID {deal_id} - "{deal_title}" '
            f'(pipeline="{PIPEDRIVE_PIPELINE_NAME}", stage="{PIPEDRIVE_STAGE_NAME}")'
        )

        # Step 3: Add note with full message and wedding date
        note_content = (
            f'<b>Kontaktformular-Anfrage</b><br>'
            f'<b>Seite:</b> {source_page}<br>'
            f'<b>Hochzeitstermin:</b> {wedding_date or "Nicht angegeben"}<br>'
            f'<b>Nachricht:</b><br>{message}'
        )

        note_data = {
            'content': note_content,
            'deal_id': deal_id,
            'person_id': person_id,
            'pinned_to_deal_flag': 1,
        }

        note_response = requests.post(
            f'{PIPEDRIVE_API_BASE}/notes?api_token={PIPEDRIVE_API_TOKEN}',
            json=note_data,
            headers=headers,
            timeout=10
        )

        if note_response.json().get('success'):
            logger.info(f'Pipedrive note added to deal {deal_id}')
        else:
            logger.warning(f'Pipedrive note creation failed (non-critical): {note_response.json()}')

        logger.info(
            'Pipedrive payload summary | '
            f'person={person_data} | deal={deal_data} | '
            f'note_fields={{"deal_id": {deal_id}, "person_id": {person_id}, "pinned_to_deal_flag": 1}}'
        )

        # Send email notification (always, regardless of Pipedrive success)
        send_lead_email(name, email, phone, wedding_date, message, source_page, whatsapp_consent, is_fallback=False)

        return True

    except requests.exceptions.Timeout:
        logger.error(f'Pipedrive API timeout for {email}')
        _log_lead_fallback(name, email, phone, wedding_date, message, source_page, whatsapp_consent)
        return True

    except Exception as e:
        logger.error(f'Pipedrive API error: {str(e)}', exc_info=True)
        _log_lead_fallback(name, email, phone, wedding_date, message, source_page, whatsapp_consent)
        return True

def _log_lead_fallback(name, email, phone, wedding_date, message, source_page, whatsapp_consent):
    """Log lead details when Pipedrive is unavailable and send emergency email notification."""
    logger.warning('=' * 60)
    logger.warning('PIPEDRIVE UNAVAILABLE - LEAD LOGGED AS FALLBACK')
    logger.warning('=' * 60)
    logger.warning(f'Source: {source_page}')
    logger.warning(f'Name: {name}')
    logger.warning(f'Email: {email}')
    logger.warning(f'Phone: {phone}')
    logger.warning(f'Wedding Date: {wedding_date or "Not specified"}')
    logger.warning(f'Message: {message}')
    logger.warning(f'WhatsApp Consent: {"accepted" if whatsapp_consent else "not accepted"}')
    logger.warning('=' * 60)
    # Send emergency email so no lead is lost even when Pipedrive is down
    send_lead_email(name, email, phone, wedding_date, message, source_page, whatsapp_consent, is_fallback=True)


@app.route('/health')
def health():
    """Health check endpoint for monitoring."""
    return {'status': 'healthy', 'service': 'hochzeitsanzug-landing'}, 200


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded."""
    logger.warning(f'🚫 Rate limit exceeded: {request.remote_addr}')
    return jsonify({
        'success': False,
        'message': 'Zu viele Anfragen. Bitte versuchen Sie es in einigen Minuten erneut.'
    }), 429


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('hochzeitsanzug.html'), 200  # Redirect all to landing page


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
