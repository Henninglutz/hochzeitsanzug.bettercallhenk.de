# Hochzeitsanzug Osnabrück - Landing Page

**High-converting landing page for bettercallhenk's wedding suit business**

Optimized for both human users and AI/LLM search engines (Generative Engine Optimization - GEO).

🌐 **Live:** [hochzeitsanzug.bettercallhenk.de](https://hochzeitsanzug.bettercallhenk.de)

---

## 🎯 Features

### For Human Users
✅ **Conversion-Optimized Design**
- Clear value proposition in hero section
- Multiple strategically placed CTAs
- Trust signals (4.9/5 stars, testimonials)
- Easy-to-scan layout with visual hierarchy
- Mobile-responsive design

✅ **4 Wedding Styles**
- Boho & Natural (light linens, earthy tones)
- Vintage & Classic (three-piece suits)
- Black Tie & Formal (tuxedos)
- Modern & Urban (slim fit, trendy colors)

✅ **Premium Services**
- Mobile fitting service (home/office)
- JGA-Special for groomsmen (group discounts)
- Exclusive KRAFT Bamboo Boxershorts (3-pack, €49.90)

### For AI/LLM Search Engines (GEO)
✅ **Semantic HTML5** - Proper structure with `<header>`, `<main>`, `<section>`, `<article>`, `<footer>`

✅ **JSON-LD Structured Data**
- `ClothingStore` schema (business info, opening hours, location)
- `FAQPage` schema (3 questions with rich answers)

✅ **Quick-Facts Box** - AI Data Layer for easy LLM extraction:
- Price: Starting at €799
- Duration: 8-12 weeks
- Styles: 4 options
- Materials: Italian fabrics

✅ **E-E-A-T Section** - Expertise, Experience, Authority, Trust:
- 15+ years of tailoring experience
- 5-step process explanation
- Customer testimonials (4.9/5 stars)

✅ **SEO Optimized**
- Complete meta tags (title, description, keywords)
- Open Graph for social sharing
- Twitter Cards
- Canonical URLs
- Robots directives

---

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/Henninglutz/hochzeitsanzug.bettercallhenk.de.git
cd hochzeitsanzug.bettercallhenk.de

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Open browser
# Navigate to: http://localhost:8000
```

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at: http://localhost:8000
```

---

## 📦 Deployment

### Railway (Recommended) ⭐

1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `hochzeitsanzug.bettercallhenk.de`
5. Railway auto-detects Flask app
6. Add environment variables:
   - `SECRET_KEY` (generate with `openssl rand -base64 32`)
7. Add custom domain: `hochzeitsanzug.bettercallhenk.de`

### Render

1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect GitHub repo
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3.11
5. Add environment variable: `SECRET_KEY`
6. Add custom domain

### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create hochzeitsanzug-landing

# Set environment variables
heroku config:set SECRET_KEY=$(openssl rand -base64 32)

# Deploy
git push heroku main

# Open app
heroku open
```

### Docker Deployment

```bash
# Build image
docker build -t hochzeitsanzug-landing .

# Run container
docker run -d \
  -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  --name hochzeitsanzug \
  hochzeitsanzug-landing

# Check health
curl http://localhost:8000/health
```

---

## 🛠️ Customization

### Update Contact Information

Edit `templates/hochzeitsanzug.html`:

```html
<!-- Line 69: Phone number -->
"telephone": "+49-541-YOUR-NUMBER",

<!-- Line 146: CTA button -->
<a href="tel:+49541YOURNUMBER" class="btn btn-secondary btn-lg">

<!-- Line 474: Email -->
<a href="mailto:YOUR-EMAIL@bettercallhenk.de" class="btn btn-secondary btn-lg">
```

### Add Images

Place images in `static/images/`:

- `hero-wedding-suit.jpg` (600x800px)
- `style-boho.jpg` (400x500px)
- `style-vintage-classic.jpeg` (400x500px)
- `style-blacktie.jpg` (400x500px)
- `style-modern-urban.jpg` (400x500px)
- `style-tweed-outdoor.jpeg` (400x500px)

See `static/images/README.md` for specifications.

### Add Analytics

Add to `<head>` section in `templates/hochzeitsanzug.html`:

**Google Analytics (GA4):**
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

**Plausible Analytics:**
```html
<script defer data-domain="hochzeitsanzug.bettercallhenk.de" src="https://plausible.io/js/script.js"></script>
```

---

## 🎨 Tech Stack

- **Backend:** Flask 3.0 with Gunicorn WSGI server
- **Frontend:** Vanilla JavaScript (no frameworks)
- **Styling:** CSS3 with custom properties
- **Deployment:** Docker, Railway, Render, Heroku
- **SEO:** JSON-LD structured data, Schema.org
- **Analytics:** Google Analytics & Plausible ready

---

## 📊 SEO & Keywords

### Primary Keywords
- Hochzeitsanzug Osnabrück
- Bräutigam Anzug
- Maßanzug Hochzeit
- Wedding Suit

### Secondary Keywords
- Anzug nach Maß Osnabrück
- Hochzeitsanzug kaufen
- Bräutigam Mode
- Smoking Hochzeit

### JSON-LD Schemas
- `ClothingStore` - Business information
- `FAQPage` - Rich snippets for questions

### Structured Data Testing
- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Schema.org Validator](https://validator.schema.org/)

---

## 🧪 Testing

### Manual Testing Checklist

**SEO:**
- [ ] Google Rich Results Test passes
- [ ] Schema.org validation passes
- [ ] Meta tags preview correctly on social media

**Performance:**
- [ ] Google PageSpeed Insights score >90
- [ ] Mobile-Friendly Test passes
- [ ] All images optimized (<200KB)

**Accessibility:**
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] WCAG 2.1 AA compliant

**Cross-Browser:**
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari (desktop & mobile)
- [ ] Mobile (iOS & Android)

---

## 📈 Analytics & Tracking

The landing page tracks:
- FAQ interactions (expand/collapse)
- CTA button clicks
- Phone link clicks
- Email link clicks
- Section scroll visibility
- Navigation usage

All tracking is handled by `hochzeitsanzug.js` and integrates with:
- Google Analytics (GA4)
- Plausible Analytics

---

## 🔒 Security

- Environment variables for sensitive data
- CORS configured for production
- Secret key rotation recommended
- HTTPS enforced (via deployment platform)

---

## 📝 Content Management

### Adding FAQ Items

Edit `templates/hochzeitsanzug.html` in the FAQ section:

```html
<article class="faq-item">
  <button class="faq-question" aria-expanded="false">
    <span class="faq-question-text">Your Question?</span>
    <span class="faq-icon" aria-hidden="true">+</span>
  </button>
  <div class="faq-answer" hidden>
    <p>Your answer here.</p>
  </div>
</article>
```

Don't forget to update the JSON-LD schema at the top!

---

## 🚧 Future Enhancements

- [ ] Add booking/appointment system
- [ ] Integrate with CRM
- [ ] Add customer review widget
- [ ] Implement A/B testing
- [ ] Add live chat support
- [ ] Create blog for content marketing
- [ ] Add multi-language support (English)

---

## 📄 License

Proprietary - © 2025 bettercallhenk. All rights reserved.

---

## 🙋 Support

For questions or issues:
- **Email:** info@bettercallhenk.de
- **Phone:** +49-541-12345678
- **Business Hours:** Mon-Sat 10:00-18:00

---

**Built with ❤️ for bettercallhenk**
