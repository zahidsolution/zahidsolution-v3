// =====================
// Typing Effect (Hero Section)
// =====================
document.addEventListener("DOMContentLoaded", () => {
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
    // Scroll Progress Bar
    // =====================
    const scrollProgress = document.getElementById("scroll-progress");
    if (scrollProgress) {
        window.addEventListener("scroll", () => {
            const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = (window.scrollY / totalHeight) * 100;
            scrollProgress.style.width = progress + "%";
        });
    }

    // =====================
    // Skill Bar Animation
    // =====================
    const skillBars = document.querySelectorAll(".skill-fill");
    const skillObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.width = entry.target.dataset.skill;
                skillObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    skillBars.forEach(bar => {
        bar.style.transition = "width 1s ease";
        skillObserver.observe(bar);
    });

    // =====================
    // Fetch Latest Blogs (API) - Optional
    // =====================
    const blogContainer = document.getElementById("latest-blogs");
    if (blogContainer) {
        blogContainer.innerHTML = "<p>Loading blogs...</p>";
        fetch("/api/blog")
            .then(res => res.json())
            .then(data => {
                blogContainer.innerHTML = "";
                if (data.blogs.length > 0) {
                    data.blogs.forEach(blog => {
                        const blogItem = document.createElement("div");
                        blogItem.classList.add("blog-card");
                        blogItem.innerHTML = `
                            <h4><a href="/blog/${blog.slug}">${blog.title}</a></h4>
                            <p>${blog.content.substring(0, 120)}...</p>
                            <a href="/blog/${blog.slug}" class="btn btn-sm btn-primary mt-2">Read More</a>
                        `;
                        blogContainer.appendChild(blogItem);
                    });
                } else {
                    blogContainer.innerHTML = "<p>No blogs available.</p>";
                }
            })
            .catch(() => {
                blogContainer.innerHTML = "<p>Failed to load blogs. Try again later.</p>";
            });
    }

    // =====================
    // Animated Stats Counter
    // =====================
    const counters = document.querySelectorAll(".counter");
    const counterObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = +counter.dataset.target;
                let count = 0;
                const speed = 50;
                const increment = target / speed;

                const updateCount = () => {
                    if (count < target) {
                        count += increment;
                        counter.innerText = Math.ceil(count);
                        setTimeout(updateCount, 30);
                    } else {
                        counter.innerText = target;
                    }
                };
                updateCount();
                counterObserver.unobserve(counter);
            }
        });
    });
    counters.forEach(counter => counterObserver.observe(counter));

    // =====================
    // Chatbot Toggle
    // =====================
    const chatToggle = document.getElementById("chat-toggle");
    const chatWindow = document.getElementById("chat-window");
    const sendBtn = document.getElementById("send-btn");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");

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

        fetch("/api/chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        })
            .then(res => res.json())
            .then(data => {
                const botMsg = document.createElement("div");
                botMsg.textContent = "Bot: " + (data?.reply || "Sorry, I didn’t get that.");
                chatMessages.appendChild(botMsg);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            })
            .catch(() => {
                const botMsg = document.createElement("div");
                botMsg.textContent = "Bot: Sorry, I can't connect right now.";
                chatMessages.appendChild(botMsg);
            });
    }

    // =====================
    // Back-to-Top Button
    // =====================
    const backToTopBtn = document.querySelector(".back-to-top");
    if (backToTopBtn) {
        backToTopBtn.style.transition = "opacity 0.3s";
        window.addEventListener("scroll", () => {
            backToTopBtn.style.opacity = window.scrollY > 300 ? "1" : "0";
            backToTopBtn.style.pointerEvents = window.scrollY > 300 ? "auto" : "none";
        });
    }

    // =====================
    // Smooth Scroll
    // =====================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", e => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute("href"));
            if (target) target.scrollIntoView({ behavior: "smooth" });
        });
    });

    // =====================
    // Dark/Light Mode Toggle with Persistence
    // =====================
    const toggleThemeBtn = document.createElement("button");
    toggleThemeBtn.innerText = "🌙";
    Object.assign(toggleThemeBtn.style, {
        position: "fixed",
        bottom: "80px",
        right: "20px",
        background: "#3b82f6",
        color: "#fff",
        border: "none",
        borderRadius: "50%",
        width: "50px",
        height: "50px",
        cursor: "pointer",
        zIndex: "999"
    });
    document.body.appendChild(toggleThemeBtn);

    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        toggleThemeBtn.innerText = "☀️";
    }

    toggleThemeBtn.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
        const isDark = document.body.classList.contains("dark-mode");
        toggleThemeBtn.innerText = isDark ? "☀️" : "🌙";
        localStorage.setItem("theme", isDark ? "dark" : "light");
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
    if (navbar) {
        window.addEventListener("scroll", () => {
            navbar.classList.toggle("scrolled", window.scrollY > 50);
        });
    }

    // =====================
    // Newsletter Form Validation
    // =====================
    const newsletterForm = document.querySelector(".newsletter-section form");
    if (newsletterForm) {
        newsletterForm.addEventListener("submit", e => {
            const emailInput = newsletterForm.querySelector("input[type='email']");
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value)) {
                e.preventDefault();
                alert("Please enter a valid email address.");
            }
        });
    }

    // =====================
    // Get Started Button Glow
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
    const lazyElements = document.querySelectorAll("img[data-src], video[data-src]");
    const lazyObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                if (el.dataset.src) el.src = el.dataset.src;
                lazyObserver.unobserve(el);
            }
        });
    });
    lazyElements.forEach(el => lazyObserver.observe(el));
});
