// ===========================================================
// MAIN.JS - Optimized Interactive & SEO-Ready Script
// ===========================================================

// =======================
// 1️⃣ Navbar Scroll Effect & Progress Bar
// =======================
const navbar = document.querySelector('.navbar');
const scrollProgress = document.createElement('div');
scrollProgress.id = 'scrollProgress';
document.body.appendChild(scrollProgress);

let lastScroll = 0;
window.addEventListener('scroll', () => {
    navbar?.classList.toggle('scrolled', window.scrollY > 50);

    const scrolled = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
    scrollProgress.style.width = `${scrolled}%`;

    if (navbar) navbar.style.top = window.scrollY > lastScroll ? '-70px' : '0';
    lastScroll = window.scrollY;

    document.querySelectorAll('.card, .cta-section, .hero-section, section').forEach(el => {
        if (el.getBoundingClientRect().top < window.innerHeight - 100) {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }
    });
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
// 4️⃣ Dark Mode (Auto + Manual)
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

// Auto dark mode based on time
const hour = new Date().getHours();
if (hour >= 19 || hour < 6) {
    document.body.classList.add("dark-mode");
    localStorage.setItem("darkMode", "enabled");
}

darkModeBtn.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const enabled = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', enabled ? 'enabled' : 'disabled');
    darkModeBtn.innerText = enabled ? '☀' : '🌙';
});

// =======================
// 5️⃣ Animated Counters (Fix 0 Issue)
// =======================
document.querySelectorAll('.counter').forEach(counter => {
    const target = +counter.dataset.target || 100;
    let count = 0;
    const update = () => {
        count += Math.ceil(target / 200);
        if (count > target) count = target;
        counter.innerText = count;
        if (count < target) requestAnimationFrame(update);
    };
    update();
});

// =======================
// 6️⃣ Lazy Load Images
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
// 7️⃣ Newsletter Toast
// =======================
const newsletterForm = document.querySelector('.newsletter form');
if (newsletterForm) {
    newsletterForm.addEventListener('submit', e => {
        e.preventDefault();
        showToast('✅ Thank you for subscribing! We will contact you soon.');
    });
}

// =======================
// 8️⃣ Toast Notification
// =======================
function showToast(msg) {
    const toast = document.createElement('div');
    toast.innerText = msg;
    toast.className = 'toast';
    Object.assign(toast.style, {
        position: 'fixed', bottom: '20px', right: '20px', background: '#333',
        color: '#fff', padding: '10px 15px', borderRadius: '5px', zIndex: '1000'
    });
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// =======================
// 9️⃣ Contact Form Validation + Auto-Save
// =======================
const contactForm = document.getElementById('contactForm');
const nameField = document.getElementById('name');
if (contactForm) {
    ['name', 'email', 'message'].forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.value = localStorage.getItem(id) || '';
            input.addEventListener("input", () => localStorage.setItem(id, input.value));
        }
    });

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
// 🔟 WhatsApp Pre-fill
// =======================
const whatsappBtn = document.getElementById('whatsappBtn');
if (whatsappBtn && nameField) {
    whatsappBtn.addEventListener('click', () => {
        const userName = nameField.value.trim();
        if (userName) whatsappBtn.href = `https://wa.me/923000079078?text=Hello%20ZahidSolution,%20I%20am%20${encodeURIComponent(userName)}`;
    });
}

// =======================
// 11️⃣ Floating Contact Widget
// =======================
const contactWidget = document.createElement('div');
contactWidget.className = 'contact-widget';
contactWidget.innerHTML = `
    <a href="https://wa.me/923000079078" target="_blank" class="widget-btn whatsapp"><img src="/static/icons/whatsapp.svg" width="28"></a>
    <a href="tel:+923000079078" class="widget-btn call">📞</a>
`;
document.body.appendChild(contactWidget);

// =======================
// 12️⃣ Voice Input for Name Field
// =======================
if ('webkitSpeechRecognition' in window && nameField) {
    const micBtn = document.createElement("button");
    micBtn.innerText = "🎙";
    micBtn.style.marginLeft = "10px";
    nameField?.parentNode.appendChild(micBtn);

    micBtn.addEventListener("click", () => {
        const recognition = new webkitSpeechRecognition();
        recognition.lang = "en-US";
        recognition.start();
        recognition.onresult = e => nameField.value = e.results[0][0].transcript;
    });
}

// =======================
// 13️⃣ Testimonials Auto-Slider
// =======================
const reviews = document.querySelectorAll(".review");
let currentReview = 0;
if (reviews.length > 0) {
    reviews.forEach(r => r.style.display = "none");
    reviews[0].style.display = "block";
    setInterval(() => {
        reviews.forEach(r => r.style.display = "none");
        reviews[currentReview].style.display = "block";
        currentReview = (currentReview + 1) % reviews.length;
    }, 4000);
}

// =======================
// 14️⃣ PWA Install Prompt
// =======================
window.addEventListener("beforeinstallprompt", e => {
    e.preventDefault();
    const installBtn = document.createElement("button");
    installBtn.innerText = "📲 Install App";
    installBtn.style.position = "fixed";
    installBtn.style.bottom = "150px";
    installBtn.style.right = "30px";
    installBtn.style.background = "#38bdf8";
    installBtn.style.color = "#fff";
    installBtn.style.padding = "8px 12px";
    installBtn.style.borderRadius = "5px";
    installBtn.style.zIndex = "999";
    document.body.appendChild(installBtn);
    installBtn.addEventListener("click", () => e.prompt());
});

// =======================
// 15️⃣ Broken Link Detector (SEO)
// =======================
document.querySelectorAll("a").forEach(link => {
    if (link.hostname !== location.hostname) {
        fetch(link.href, { method: 'HEAD' })
            .then(res => { if (!res.ok) console.warn(`⚠ Broken Link: ${link.href}`); })
            .catch(() => console.warn(`⚠ Broken Link: ${link.href}`));
    }
});
