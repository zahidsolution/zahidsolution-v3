// =====================
// Typing Effect (Hero Section)
// =====================
const textArray = [
    "Transform Your Ideas Into Reality",
    "Web Development | Graphic Design | Video Editing",
    "Your Digital Success Starts Here"
];
let textIndex = 0;
let charIndex = 0;
const typingElement = document.getElementById("typing-text");

function typeEffect() {
    if (!typingElement) return;
    if (charIndex < textArray[textIndex].length) {
        typingElement.textContent += textArray[textIndex].charAt(charIndex);
        charIndex++;
        setTimeout(typeEffect, 80);
    } else {
        setTimeout(() => {
            typingElement.textContent = "";
            charIndex = 0;
            textIndex = (textIndex + 1) % textArray.length;
            typeEffect();
        }, 2000);
    }
}
typeEffect();

// =====================
// Animated Stats Counter
// =====================
const counters = document.querySelectorAll(".counter");
counters.forEach(counter => {
    const updateCount = () => {
        const target = +counter.getAttribute("data-target");
        const count = +counter.innerText;
        const speed = 50; 
        const increment = target / speed;
        if (count < target) {
            counter.innerText = Math.ceil(count + increment);
            setTimeout(updateCount, 30);
        } else {
            counter.innerText = target;
        }
    };
    const observer = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting) {
            updateCount();
            observer.disconnect();
        }
    });
    observer.observe(counter);
});

// =====================
// Chatbot Toggle
// =====================
const chatToggle = document.getElementById("chat-toggle");
const chatWindow = document.getElementById("chat-window");
const sendBtn = document.getElementById("send-btn");
const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");

const botReplies = [
    "I'm a bot, but I code better than some humans 😎",
    "Did you try turning it off and on again?",
    "404: Boring answer not found 😂",
    "I run on coffee and JavaScript ☕",
    "Beep bop! I'm here to help, or at least try...",
    "Web problems? More like web adventures! 🚀",
    "Don't worry, even Google started small 😉"
];

if (chatToggle && chatWindow) {
    chatToggle.addEventListener("click", () => {
        chatWindow.style.display = chatWindow.style.display === "block" ? "none" : "block";
    });
}

if (sendBtn && chatInput && chatMessages) {
    sendBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", e => { if (e.key === "Enter") sendMessage(); });
}

function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    const userMsg = document.createElement("div");
    userMsg.textContent = "You: " + message;
    chatMessages.appendChild(userMsg);

    chatInput.value = "";
    chatMessages.scrollTop = chatMessages.scrollHeight;

    setTimeout(() => {
        const botMsg = document.createElement("div");
        botMsg.textContent = "Bot: " + botReplies[Math.floor(Math.random() * botReplies.length)];
        chatMessages.appendChild(botMsg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 500);
}

// =====================
// Back-to-Top Button
// =====================
const backToTopBtn = document.querySelector(".back-to-top");
window.addEventListener("scroll", () => {
    if (window.scrollY > 300) {
        backToTopBtn.style.display = "block";
    } else {
        backToTopBtn.style.display = "none";
    }
});

// =====================
// Smooth Scroll
// =====================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", e => {
        e.preventDefault();
        document.querySelector(anchor.getAttribute("href")).scrollIntoView({
            behavior: "smooth"
        });
    });
});

// =====================
// Dark/Light Mode Toggle
// =====================
const toggleThemeBtn = document.createElement("button");
toggleThemeBtn.innerText = "🌙";
toggleThemeBtn.style.position = "fixed";
toggleThemeBtn.style.bottom = "80px";
toggleThemeBtn.style.right = "20px";
toggleThemeBtn.style.background = "#3b82f6";
toggleThemeBtn.style.color = "#fff";
toggleThemeBtn.style.border = "none";
toggleThemeBtn.style.borderRadius = "50%";
toggleThemeBtn.style.width = "50px";
toggleThemeBtn.style.height = "50px";
toggleThemeBtn.style.cursor = "pointer";
toggleThemeBtn.style.zIndex = "999";
document.body.appendChild(toggleThemeBtn);

toggleThemeBtn.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
    toggleThemeBtn.innerText = document.body.classList.contains("dark-mode") ? "☀️" : "🌙";
});

// =====================
// Portfolio Filter Animation
// =====================
const portfolioItems = document.querySelectorAll(".portfolio-item");
const filterButtons = document.querySelectorAll("[data-filter]");

filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        const filter = btn.getAttribute("data-filter");
        portfolioItems.forEach(item => {
            item.style.display = (filter === "all" || item.dataset.category === filter) ? "block" : "none";
        });
    });
});

// =====================
// Sticky Navbar on Scroll
// =====================
const navbar = document.querySelector(".navbar");
window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
        navbar.classList.add("scrolled");
    } else {
        navbar.classList.remove("scrolled");
    }
});

// =====================
// Newsletter Form Validation
// =====================
const newsletterForm = document.querySelector(".newsletter-section form");
if (newsletterForm) {
    newsletterForm.addEventListener("submit", e => {
        const emailInput = newsletterForm.querySelector("input[type='email']");
        if (!emailInput.value.includes("@") || !emailInput.value.includes(".")) {
            e.preventDefault();
            alert("Please enter a valid email address.");
        }
    });
}

// =====================
// Fix for Get Started Button Glow
// =====================
const getStartedBtn = document.querySelector(".btn-get-started");
if (getStartedBtn) {
    getStartedBtn.addEventListener("mouseenter", () => getStartedBtn.classList.add("active"));
    getStartedBtn.addEventListener("mouseleave", () => getStartedBtn.classList.remove("active"));
}

// =====================
// FAQ Auto-Collapse
// =====================
const faqButtons = document.querySelectorAll(".accordion-button");
faqButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        faqButtons.forEach(b => {
            if (b !== btn) {
                const collapse = b.closest(".accordion-item").querySelector(".accordion-collapse");
                if (collapse.classList.contains("show")) {
                    collapse.classList.remove("show");
                }
            }
        });
    });
});

// =====================
// Lazy Loading for Images and Videos
// =====================
const lazyElements = document.querySelectorAll("img, video");
const lazyObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const el = entry.target;
            if (el.dataset.src) {
                el.src = el.dataset.src;
            }
            lazyObserver.unobserve(el);
        }
    });
});
lazyElements.forEach(el => {
    if (el.hasAttribute("data-src")) {
        lazyObserver.observe(el);
    }
});
