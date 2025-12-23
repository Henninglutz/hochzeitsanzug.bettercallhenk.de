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

})();
