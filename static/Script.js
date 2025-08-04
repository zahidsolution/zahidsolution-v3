// =======================
// 1️⃣ Navbar Scroll Effect & Progress Bar
// =======================
const navbar = document.querySelector('.navbar');
const scrollProgress = document.createElement('div');
scrollProgress.id = 'scrollProgress';
document.body.appendChild(scrollProgress);

let lastScroll = 0;
window.addEventListener('scroll', () => {
    // Navbar scroll effect
    navbar?.classList.toggle('scrolled', window.scrollY > 50);

    // Scroll progress bar
    const scrolled = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
    scrollProgress.style.width = `${scrolled}%`;

    // Auto-hide navbar
    if (navbar) navbar.style.top = window.scrollY > lastScroll ? '-70px' : '0';
    lastScroll = window.scrollY;

    // Reveal animations
    document.querySelectorAll('.card, .cta-section, .hero-section, section').forEach(el => {
        if (el.getBoundingClientRect().top < window.innerHeight - 100) {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }
    });

    // Animated counters
    document.querySelectorAll('.counter').forEach(counter => {
        if (!counter.dataset.animated && counter.getBoundingClientRect().top < window.innerHeight) {
            counter.dataset.animated = true;
            let target = +counter.dataset.target;
            let count = 0;
            const update = () => {
                count += Math.ceil(target / 200);
                if (count > target) count = target;
                counter.innerText = count;
                if (count < target) requestAnimationFrame(update);
            };
            update();
        }
    });

    // SEO event
    console.log("SEO Event: User Scrolling");
});

// =======================
// 2️⃣ Smooth Scroll for Nav Links
// =======================
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', e => {
        if (link.hash) {
            e.preventDefault();
            document.querySelector(link.hash)?.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// =======================
// 3️⃣ Back-to-Top Button
// =======================
const backToTop = document.createElement('button');
backToTop.id = 'backToTop';
backToTop.innerText = '⬆';
document.body.appendChild(backToTop);
backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

// =======================
// 4️⃣ Dark Mode Toggle
// =======================
const darkModeBtn = document.createElement('button');
darkModeBtn.innerText = localStorage.getItem('darkMode') === 'enabled' ? '☀' : '🌙';
Object.assign(darkModeBtn.style, {
    position: 'fixed', bottom: '90px', right: '30px', background: '#0f172a',
    color: '#38bdf8', border: '2px solid #38bdf8', borderRadius: '50%',
    width: '45px', height: '45px', cursor: 'pointer', zIndex: '999'
});
document.body.appendChild(darkModeBtn);
if (localStorage.getItem('darkMode') === 'enabled') document.body.classList.add('dark-mode');

darkModeBtn.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const enabled = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', enabled ? 'enabled' : 'disabled');
    darkModeBtn.innerText = enabled ? '☀' : '🌙';
});

// =======================
// 5️⃣ Ripple Effect for Buttons
// =======================
document.querySelectorAll('.btn-get-started').forEach(btn => {
    btn.style.position = 'relative';
    btn.style.overflow = 'hidden';
    btn.addEventListener('click', e => {
        const ripple = document.createElement('span');
        Object.assign(ripple.style, {
            position: 'absolute', background: 'rgba(255,255,255,0.5)', borderRadius: '50%',
            width: '20px', height: '20px', left: `${e.offsetX}px`, top: `${e.offsetY}px`,
            transform: 'scale(0)', opacity: '0.7', animation: 'rippleAnim 0.6s linear'
        });
        btn.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    });
});
const rippleStyle = document.createElement('style');
rippleStyle.innerHTML = `@keyframes rippleAnim { to { transform: scale(8); opacity: 0; } }`;
document.head.appendChild(rippleStyle);

// =======================
// 6️⃣ Newsletter Toast
// =======================
const newsletterForm = document.querySelector('.newsletter form');
if (newsletterForm) {
    newsletterForm.addEventListener('submit', e => {
        e.preventDefault();
        showToast('✅ Thank you for subscribing! We will contact you soon.');
    });
}

// =======================
// 7️⃣ Toast Notification
// =======================
function showToast(msg) {
    const toast = document.createElement('div');
    toast.innerText = msg;
    toast.className = 'toast';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// =======================
// 8️⃣ WhatsApp Pre-fill
// =======================
const whatsappBtn = document.getElementById('whatsappBtn');
const nameField = document.getElementById('name');
if (whatsappBtn && nameField) {
    whatsappBtn.addEventListener('click', () => {
        const userName = nameField.value.trim();
        if (userName) whatsappBtn.href = `https://wa.me/923000079078?text=Hello%20ZahidSolution,%20I%20am%20${encodeURIComponent(userName)}`;
    });
}

// =======================
// 9️⃣ Contact Form Validation
// =======================
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', e => {
        e.preventDefault();
        const email = document.getElementById('email').value.trim();
        const name = nameField?.value.trim();
        const message = document.getElementById('message').value.trim();

        if (!name || !email || !message) return showToast("⚠ Please fill all fields.");
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return showToast("⚠ Invalid email address.");

        const btn = contactForm.querySelector('button');
        btn.disabled = true;
        btn.innerText = "Sending...";
        setTimeout(() => {
            btn.disabled = false;
            btn.innerText = "Send Message";
            showToast("✅ Your message has been sent!");
            contactForm.reset();
        }, 1500);
    });
}

// =======================
// 🔟 Floating Contact Widget
// =======================
const contactWidget = document.createElement('div');
contactWidget.className = 'contact-widget';
contactWidget.innerHTML = `
    <a href="https://wa.me/923000079078" target="_blank" class="widget-btn whatsapp"><img src="/static/icons/whatsapp.svg" width="28"></a>
    <a href="tel:+923000079078" class="widget-btn call">📞</a>
`;
document.body.appendChild(contactWidget);

// =======================
// 11️⃣ Save & Restore Form Data
// =======================
if (contactForm) {
    ['name', 'email', 'message'].forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.value = localStorage.getItem(id) || '';
            input.addEventListener('input', () => localStorage.setItem(id, input.value));
        }
    });
}

// =======================
// 12️⃣ Lazy Load Images
// =======================
document.querySelectorAll('img[data-src]').forEach(img => {
    new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.src = entry.target.dataset.src;
                observer.unobserve(entry.target);
            }
        });
    }).observe(img);
});

// =======================
// 13️⃣ Misc Features
// =======================
document.addEventListener('contextmenu', e => e.preventDefault()); // No right-click
window.addEventListener('online', () => showToast('✅ You are back online!'));
window.addEventListener('offline', () => showToast('⚠ You are offline!'));
document.addEventListener('visibilitychange', () => document.title = document.hidden ? 'Come back 😢' : originalTitle);
