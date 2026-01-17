"""
Hochzeitsanzug Landing Page - Standalone Flask Application
Optimized for deployment at hochzeitsanzug.bettercallhenk.de
"""

import os
import re
import time
import logging
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

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


@app.route('/danke')
def thank_you():
    """Serve the thank you page after a successful booking."""
    return render_template('danke.html')


@app.route('/api/contact', methods=['POST'])
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
        recaptcha_score = verify_recaptcha(recaptcha_token, request.remote_addr)

        if recaptcha_score is None:
            logger.warning(f'🤖 BOT DETECTED (reCAPTCHA Failed): {email}')
            # Fake success for bots
            return jsonify({
                'success': True,
                'message': 'Vielen Dank! Wir haben Ihre Anfrage erhalten.'
            }), 200

        if recaptcha_score < RECAPTCHA_SCORE_THRESHOLD:
            logger.warning(f'🤖 BOT DETECTED (Low Score): {email} - Score: {recaptcha_score}')
            # Fake success for bots
            return jsonify({
                'success': True,
                'message': 'Vielen Dank! Wir haben Ihre Anfrage erhalten.'
            }), 200

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

        # === ALL CHECKS PASSED - Real Human User ===
        logger.info(f'✅ REAL USER: {email} - reCAPTCHA Score: {recaptcha_score}')

        # Send email notification
        email_sent = send_contact_email(name, email, phone, wedding_date, message)

        if email_sent:
            logger.info(f'📧 Email sent successfully to henk@bettercallhenk.de')
            return jsonify({
                'success': True,
                'message': 'Vielen Dank! Wir haben Ihre Anfrage erhalten und melden uns bald bei Ihnen.'
            }), 200
        else:
            logger.error(f'❌ Email sending failed for {email}')
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


def send_contact_email(name, email, phone, wedding_date, message):
    """
    Send contact form notification email

    This is a placeholder function. In production, you should:
    1. Use SMTP (smtplib) to send emails
    2. Or use a service like SendGrid, Mailgun, AWS SES
    3. Or save to database and process later

    For now, we'll just log it and return True
    """
    logger.info('=' * 60)
    logger.info('📧 NEW CONTACT FORM SUBMISSION')
    logger.info('=' * 60)
    logger.info(f'Name: {name}')
    logger.info(f'Email: {email}')
    logger.info(f'Phone: {phone}')
    logger.info(f'Wedding Date: {wedding_date or "Not specified"}')
    logger.info(f'Message: {message}')
    logger.info('=' * 60)

    # TODO: Implement actual email sending
    # For production, use:
    # - SMTP with smtplib
    # - SendGrid API
    # - Mailgun API
    # - AWS SES
    # - Or save to database and send via background worker

    return True  # Placeholder - always returns success


@app.route('/health')
def health():
    """Health check endpoint for monitoring."""
    return {'status': 'healthy', 'service': 'hochzeitsanzug-landing'}, 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('hochzeitsanzug.html'), 200  # Redirect all to landing page


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
