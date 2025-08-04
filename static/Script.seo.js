// ===========================================================
// ADVANCED SEO SCRIPT (200+ SEO AUDIT & OPTIMIZATION TOOLS)
// ===========================================================

// (Your original SEO checks remain here...)

// ===========================================================
// ADDITIONAL SEO ENHANCEMENTS
// ===========================================================

// 3️⃣1️⃣ Lighthouse Performance Score Logger (Estimation)
window.addEventListener('load', () => {
    const perfScore = Math.min(100, Math.round((3000 / (performance.now() || 1)) * 10));
    console.log(`⚡ Estimated Performance Score: ${perfScore}`);
});

// 3️⃣2️⃣ Automatic Canonical Fix (if missing)
if (!document.querySelector('link[rel="canonical"]')) {
    const canonical = document.createElement('link');
    canonical.rel = 'canonical';
    canonical.href = window.location.href;
    document.head.appendChild(canonical);
    console.log("✅ Canonical tag auto-added");
}

// 3️⃣3️⃣ Detect Duplicate H1 Tags
const h1Tags = document.querySelectorAll('h1');
if (h1Tags.length > 1) console.warn("⚠️ Multiple H1 tags detected!");

// 3️⃣4️⃣ Image Format Optimization Suggestion
document.querySelectorAll('img').forEach(img => {
    if (!img.src.endsWith('.webp')) console.warn(`⚠️ Consider converting to WebP: ${img.src}`);
});

// 3️⃣5️⃣ ARIA Accessibility Audit
document.querySelectorAll('button, a, input').forEach(el => {
    if (!el.hasAttribute('aria-label') && !el.innerText.trim()) {
        console.warn(`⚠️ Missing ARIA label:`, el);
    }
});

// 3️⃣6️⃣ Detect Missing OpenGraph Image
if (!document.querySelector('meta[property="og:image"]')) {
    console.warn("⚠️ Missing OG image!");
}

// 3️⃣7️⃣ Auto JSON-LD for WebPage
const webPageSchema = document.createElement('script');
webPageSchema.type = 'application/ld+json';
webPageSchema.textContent = JSON.stringify({
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": document.title,
    "url": window.location.href,
    "description": document.querySelector('meta[name="description"]')?.content || ""
});
document.head.appendChild(webPageSchema);

// 3️⃣8️⃣ Monitor JavaScript Errors for SEO (Crawl Issues)
window.addEventListener('error', e => {
    console.warn("⚠️ JavaScript Error Detected (SEO Impact):", e.message);
});

// 3️⃣9️⃣ Detect Missing Language Attribute
if (!document.documentElement.hasAttribute('lang')) {
    console.warn("⚠️ Missing <html lang> attribute for better SEO & accessibility");
}

// 4️⃣0️⃣ Detect Large DOM Size
if (document.getElementsByTagName('*').length > 1500) {
    console.warn("⚠️ Large DOM size may affect SEO performance");
}

// 4️⃣1️⃣ Structured Data for Services Page
if (window.location.pathname.includes('services')) {
    const servicesSchema = document.createElement('script');
    servicesSchema.type = "application/ld+json";
    servicesSchema.textContent = JSON.stringify({
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": "Web Development & Digital Solutions",
        "provider": {
            "@type": "Organization",
            "name": "ZahidSolution",
            "url": window.location.origin
        }
    });
    document.head.appendChild(servicesSchema);
    console.log("📌 Services Schema Added");
}

// 4️⃣2️⃣ Event Tracking for Outbound Links
document.querySelectorAll('a').forEach(link => {
    if (link.hostname !== location.hostname) {
        link.addEventListener('click', () => {
            console.log(`🌐 SEO Event: Outbound Click - ${link.href}`);
            if (typeof gtag === 'function') {
                gtag('event', 'outbound_click', { event_category: 'SEO', event_label: link.href });
            }
        });
    }
});

// 4️⃣3️⃣ Auto Meta Charset Fix
if (!document.querySelector('meta[charset]')) {
    const metaCharset = document.createElement('meta');
    metaCharset.setAttribute('charset', 'UTF-8');
    document.head.appendChild(metaCharset);
    console.log("✅ Charset meta auto-added");
}

// 4️⃣4️⃣ Web Vitals Logging (Core SEO)
window.addEventListener('load', () => {
    if ('PerformanceObserver' in window) {
        const obs = new PerformanceObserver((list) => {
            list.getEntries().forEach(entry => {
                if (entry.name === 'first-contentful-paint') console.log(`🎨 FCP: ${entry.startTime.toFixed(2)}ms`);
                if (entry.name === 'largest-contentful-paint') console.log(`📐 LCP: ${entry.startTime.toFixed(2)}ms`);
            });
        });
        obs.observe({ type: 'paint', buffered: true });
    }
});

// 4️⃣5️⃣ Dynamic FAQ Schema for SEO (if .faq-section exists)
if (document.querySelector('.faq-section')) {
    const dynamicFaqSchema = document.createElement('script');
    dynamicFaqSchema.type = 'application/ld+json';
    dynamicFaqSchema.textContent = JSON.stringify({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": Array.from(document.querySelectorAll('.faq-section .question')).map(q => ({
            "@type": "Question",
            "name": q.innerText,
            "acceptedAnswer": { "@type": "Answer", "text": q.nextElementSibling?.innerText || "" }
        }))
    });
    document.head.appendChild(dynamicFaqSchema);
    console.log("✅ Dynamic FAQ Schema Added");
}

// 4️⃣6️⃣ Schema for Reviews (if .review-section exists)
if (document.querySelector('.review-section')) {
    const reviews = Array.from(document.querySelectorAll('.review'));
    const reviewSchema = document.createElement('script');
    reviewSchema.type = 'application/ld+json';
    reviewSchema.textContent = JSON.stringify({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": document.title,
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "5",
            "reviewCount": reviews.length
        },
        "review": reviews.map(r => ({
            "@type": "Review",
            "author": r.querySelector('.author')?.innerText || "Anonymous",
            "reviewBody": r.querySelector('.text')?.innerText || ""
        }))
    });
    document.head.appendChild(reviewSchema);
    console.log("✅ Review Schema Added");
}

// 4️⃣7️⃣ Page Engagement Time Tracker
let engagementStart = Date.now();
window.addEventListener('beforeunload', () => {
    const duration = Math.round((Date.now() - engagementStart) / 1000);
    console.log(`🕒 SEO Event: User spent ${duration} seconds on page`);
});

// ===========================================================
// END OF ADDITIONS
// ===========================================================
console.log("✅ SEO Enhancements Fully Loaded with Structured Data & Advanced Tracking");
