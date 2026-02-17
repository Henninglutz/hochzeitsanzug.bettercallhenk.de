/**
 * Hochzeitsanzug Landing Page JavaScript
 * Interactive elements and enhancements
 */

(function() {
  'use strict';

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    initFAQAccordion();
    initSmoothScroll();
    initMobileNav();
    initCTATracking();
    initIntersectionObserver();
    initContactForm();
  }

  /**
   * FAQ Accordion Functionality
   */
  function initFAQAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
      const question = item.querySelector('.faq-question');
      const answer = item.querySelector('.faq-answer');

      if (!question || !answer) return;

      question.addEventListener('click', () => {
        const isExpanded = question.getAttribute('aria-expanded') === 'true';

        // Close all other FAQ items
        faqItems.forEach(otherItem => {
          const otherQuestion = otherItem.querySelector('.faq-question');
          const otherAnswer = otherItem.querySelector('.faq-answer');
          if (otherQuestion && otherAnswer && otherItem !== item) {
            otherQuestion.setAttribute('aria-expanded', 'false');
            otherAnswer.setAttribute('hidden', '');
          }
        });

        // Toggle current item
        question.setAttribute('aria-expanded', !isExpanded);
        if (isExpanded) {
          answer.setAttribute('hidden', '');
        } else {
          answer.removeAttribute('hidden');
          trackEvent('FAQ', 'Expand', question.textContent.trim());
        }
      });
    });
  }

  /**
   * Smooth Scroll for Navigation Links
   */
  function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
      link.addEventListener('click', (e) => {
        const href = link.getAttribute('href');
        if (href === '#') return;

        const target = document.querySelector(href);
        if (!target) return;

        e.preventDefault();

        const headerOffset = 80;
        const elementPosition = target.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });

        trackEvent('Navigation', 'Click', href);
      });
    });
  }

  /**
   * Mobile Navigation Toggle
   */
  function initMobileNav() {
    // Simple implementation - can be expanded for hamburger menu
    const nav = document.querySelector('.nav');
    if (!nav) return;

    // Add mobile-friendly behavior if needed
    if (window.innerWidth <= 768) {
      console.log('Mobile navigation initialized');
    }
  }

  /**
   * CTA Click Tracking
   */
  function initCTATracking() {
    // Track primary CTA clicks
    const ctaButtons = document.querySelectorAll('.btn-primary, .btn-secondary');

    ctaButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const text = btn.textContent.trim();
        trackEvent('CTA', 'Click', text);
      });
    });

    // Track phone link clicks
    const phoneLinks = document.querySelectorAll('a[href^="tel:"]');
    phoneLinks.forEach(link => {
      link.addEventListener('click', () => {
        trackEvent('Contact', 'Phone Click', link.textContent.trim());
      });
    });

    // Track email link clicks
    const emailLinks = document.querySelectorAll('a[href^="mailto:"]');
    emailLinks.forEach(link => {
      link.addEventListener('click', () => {
        trackEvent('Contact', 'Email Click', link.textContent.trim());
      });
    });
  }

  /**
   * Intersection Observer for Scroll Animations
   */
  function initIntersectionObserver() {
    // Check if IntersectionObserver is supported
    if (!('IntersectionObserver' in window)) {
      return;
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          trackEvent('Scroll', 'Section View', entry.target.id || entry.target.className);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -100px 0px'
    });

    // Observe sections
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
      observer.observe(section);
    });
  }

  /**
   * Event Tracking Helper
   * Supports both Google Analytics and Plausible Analytics
   */
  function trackEvent(category, action, label) {
    // Google Analytics (GA4)
    if (typeof gtag === 'function') {
      gtag('event', action, {
        'event_category': category,
        'event_label': label
      });
    }

    // Plausible Analytics
    if (typeof plausible === 'function') {
      plausible(action, {
        props: {
          category: category,
          label: label
        }
      });
    }

    // Console log for debugging (remove in production)
    console.log('Event:', category, action, label);
  }

  /**
   * Lazy Load Images
   */
  function initLazyLoading() {
    if ('loading' in HTMLImageElement.prototype) {
      // Browser supports native lazy loading
      const images = document.querySelectorAll('img[loading="lazy"]');
      images.forEach(img => {
        img.src = img.dataset.src || img.src;
      });
    } else {
      // Fallback for browsers that don't support lazy loading
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
      document.body.appendChild(script);
    }
  }

  // Initialize lazy loading
  initLazyLoading();

  /**
   * Contact Form with Anti-Spam Protection
   * - reCAPTCHA v3
   * - Honeypot field
   * - Timestamp check (< 5 sec = bot)
   * - German phone validation
   */
  function initContactForm() {
    const form = document.getElementById('contact-form');
    if (!form) return;

    const formLoadedAtField = document.getElementById('form_loaded_at');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnSpinner = submitBtn.querySelector('.btn-spinner');
    const formMessage = document.getElementById('form-message');

    // Set timestamp when form loads
    if (formLoadedAtField) {
      formLoadedAtField.value = Date.now().toString();
    }

    // German phone validation regex
    // Akzeptiert: +49, 0049, 0... (Deutsche Nummern)
    const germanPhoneRegex = /^(\+49|0049|0)[1-9]\d{1,14}$/;

    // Form submit handler
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      // Clear previous errors
      clearErrors();
      hideMessage();

      // Client-side validation
      if (!validateForm()) {
        return;
      }

      // Disable submit button
      submitBtn.disabled = true;
      btnText.style.display = 'none';
      btnSpinner.style.display = 'inline';

      try {
        // Get reCAPTCHA token
        const recaptchaToken = await getRecaptchaToken();

        // Prepare form data
        const formData = new FormData(form);
        const data = {
          name: formData.get('name'),
          email: formData.get('email'),
          phone: formData.get('phone'),
          wedding_date: formData.get('wedding_date'),
          message: formData.get('message'),
          website: formData.get('website'), // Honeypot
          form_loaded_at: formData.get('form_loaded_at'),
          recaptcha_token: recaptchaToken,
          source: formData.get('source') || 'unknown'
        };

        // Send to backend
        const response = await fetch('/api/contact', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok && result.success) {
          // Success - redirect to thank you page
          showMessage('Vielen Dank! Wir haben Ihre Anfrage erhalten.', 'success');
          form.reset();

          // Redirect after 1.5 seconds
          setTimeout(() => {
            window.location.href = '/danke';
          }, 1500);
        } else if (response.status === 429) {
          // Rate limited
          showMessage(
            'Zu viele Anfragen. Bitte versuchen Sie es in einigen Minuten erneut.',
            'error'
          );
        } else {
          // Other error
          showMessage(
            result.message || 'Es ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.',
            'error'
          );
        }
      } catch (error) {
        console.error('Form submission error:', error);
        showMessage(
          'Es gab ein Problem bei der Verbindung. Bitte versuchen Sie es erneut oder rufen Sie uns direkt an unter +49 160 78 57 633.',
          'error'
        );
      } finally {
        // Re-enable submit button
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnSpinner.style.display = 'none';
      }
    });

    /**
     * Get reCAPTCHA v3 Token
     * Returns null if reCAPTCHA is not available (adblocker, network issue, etc.)
     * The backend will still validate via honeypot, timestamp, and phone checks
     */
    function getRecaptchaToken() {
      return new Promise((resolve) => {
        if (typeof grecaptcha === 'undefined') {
          console.warn('reCAPTCHA not available - submitting without token');
          resolve(null);
          return;
        }

        // Timeout safety: if reCAPTCHA hangs, resolve after 5 seconds
        var timeout = setTimeout(function() { resolve(null); }, 5000);

        try {
          grecaptcha.ready(() => {
            grecaptcha
              .execute('6Ld6h00sAAAAAFtzUGxEg2qj-jY73bYFRcNYjsWt', { action: 'contact_form' })
              .then((token) => {
                clearTimeout(timeout);
                resolve(token);
              })
              .catch((err) => {
                clearTimeout(timeout);
                console.warn('reCAPTCHA execute failed:', err);
                resolve(null);
              });
          });
        } catch (err) {
          clearTimeout(timeout);
          console.warn('reCAPTCHA ready() failed:', err);
          resolve(null);
        }
      });
    }

    /**
     * Client-side form validation
     */
    function validateForm() {
      let isValid = true;

      // Name validation
      const name = form.querySelector('#name').value.trim();
      if (name.length < 2) {
        showError('name', 'Bitte geben Sie Ihren vollständigen Namen ein.');
        isValid = false;
      }

      // Email validation
      const email = form.querySelector('#email').value.trim();
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        showError('email', 'Bitte geben Sie eine gültige E-Mail-Adresse ein.');
        isValid = false;
      }

      // German phone validation
      const phone = form.querySelector('#phone').value.trim().replace(/\s/g, '');
      if (!germanPhoneRegex.test(phone)) {
        showError(
          'phone',
          'Bitte geben Sie eine gültige deutsche Telefonnummer ein (z.B. 0160 1234567 oder +49 160 1234567).'
        );
        isValid = false;
      }

      // Message validation
      const message = form.querySelector('#message').value.trim();
      if (message.length < 10) {
        showError('message', 'Bitte geben Sie eine ausführlichere Nachricht ein (mind. 10 Zeichen).');
        isValid = false;
      }

      return isValid;
    }

    /**
     * Show validation error
     */
    function showError(fieldName, message) {
      const errorElement = document.getElementById(`${fieldName}-error`);
      if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
      }

      const inputElement = document.getElementById(fieldName);
      if (inputElement) {
        inputElement.classList.add('error');
        inputElement.setAttribute('aria-invalid', 'true');
      }
    }

    /**
     * Clear all errors
     */
    function clearErrors() {
      const errorElements = form.querySelectorAll('.form-error');
      errorElements.forEach(el => {
        el.textContent = '';
        el.style.display = 'none';
      });

      const inputElements = form.querySelectorAll('.error');
      inputElements.forEach(el => {
        el.classList.remove('error');
        el.removeAttribute('aria-invalid');
      });
    }

    /**
     * Show form message
     */
    function showMessage(message, type) {
      formMessage.textContent = message;
      formMessage.className = `form-message form-message--${type}`;
      formMessage.style.display = 'block';

      // Track event
      trackEvent('Form', 'Submit', type === 'success' ? 'Success' : 'Error');
    }

    /**
     * Hide form message
     */
    function hideMessage() {
      formMessage.style.display = 'none';
    }
  }

})();
