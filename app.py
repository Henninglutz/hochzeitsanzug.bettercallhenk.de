"""
Hochzeitsanzug Landing Page - Standalone Flask Application
Optimized for deployment at hochzeitsanzug.bettercallhenk.de
"""

import os
from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
app.url_map.strict_slashes = False

# CORS Configuration
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'


@app.route('/')
@app.route('/LP-Hochzeitsanzug')
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
@app.route('/LP-Hochzeitsanzug/danke')
def thank_you():
    """Serve the thank you page after a successful booking."""
    return render_template('danke.html')


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
