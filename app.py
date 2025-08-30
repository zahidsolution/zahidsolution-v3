from flask import Flask, render_template, request, redirect, flash, jsonify
import sqlite3
import os
from slugify import slugify
import openai
import logging
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app = Flask(__name__)
app.secret_key = "zahid_secret_key"

# =========================
# Upload Folder
# =========================
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# =========================
# OpenAI API Setup
# =========================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY not found in environment variables.")
openai.api_key = OPENAI_API_KEY

# =========================
# Logging
# =========================
logging.basicConfig(level=logging.INFO)

# =========================
# Database Initialization
# =========================
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            message TEXT,
            rating INTEGER DEFAULT 0,
            reply TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            file TEXT,
            media_type TEXT,
            category TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS newsletter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            slug TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# =========================
# SEO Utility
# =========================
def get_seo_data(page, title=None, description=None, keywords=None):
    defaults = {
        "title": "ZahidSolution - Web Development, Design & Editing",
        "description": "Professional web development, graphic design, and video editing services for your business success.",
        "keywords": "web development, graphic design, video editing, ZahidSolution, portfolio, Pakistan"
    }
    return {
        "title": title or defaults["title"],
        "description": description or defaults["description"],
        "keywords": keywords or (title if title else defaults["keywords"])
    }

# =========================
# Routes
# =========================
@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, message, rating FROM feedback ORDER BY id DESC LIMIT 5")
    feedbacks = cursor.fetchall()
    conn.close()
    seo = get_seo_data("home", "Welcome to ZahidSolution", "Professional Web, Video, and Graphic Solutions")
    return render_template('index.html', seo=seo, feedbacks=feedbacks)

# =========================
# Blog
# =========================
@app.route('/admin/blog', methods=['GET', 'POST'])
def admin_blog():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        slug = slugify(title)
        cursor.execute("INSERT INTO blog (title, content, slug) VALUES (?, ?, ?)", (title, content, slug))
        conn.commit()
    cursor.execute("SELECT * FROM blog ORDER BY id DESC")
    posts = cursor.fetchall()
    conn.close()
    return render_template('admin_blog.html', blog_posts=posts)

@app.route('/blog/<slug>')
def blog_detail(slug):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blog WHERE slug=?", (slug,))
    post = cursor.fetchone()
    conn.close()
    if not post:
        return redirect('/')
    seo = get_seo_data("blog", post[1], post[2][:160])
    return render_template('blog_detail.html', blog=post, seo=seo)

# =========================
# Newsletter
# =========================
@app.route('/newsletter', methods=['POST'])
def newsletter():
    email = request.form['email']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO newsletter (email) VALUES (?)", (email,))
        conn.commit()
        flash("Thanks for subscribing!", "success")
    except sqlite3.IntegrityError:
        flash("You are already subscribed!", "info")
    conn.close()
    return redirect('/')

# =========================
# Feedback
# =========================
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    seo = get_seo_data("feedback", "Customer Feedback", "See what clients say about ZahidSolution.")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name') or "Anonymous"
        email = request.form.get('email')
        message = request.form.get('message')
        rating = int(request.form.get('rating') or 0)
        honeypot = request.form.get('honeypot')

        if honeypot:
            return jsonify({"error": "Spam detected."})
        if not email or not message:
            return jsonify({"error": "Email and message required."})

        cursor.execute(
            "INSERT INTO feedback (name, email, message, rating, submitted_at) VALUES (?, ?, ?, ?, datetime('now'))",
            (name, email, message, rating)
        )
        conn.commit()
        cursor.execute("SELECT datetime('now')")
        date = cursor.fetchone()[0]
        conn.close()

        return jsonify({"success": True, "name": name, "message": message, "rating": rating, "date": date})

    cursor.execute("SELECT name, email, message, rating, submitted_at FROM feedback ORDER BY id DESC")
    feedbacks = cursor.fetchall()
    conn.close()
    return render_template('feedback.html', seo=seo, feedbacks=feedbacks)

# =========================
# Chatbot
# =========================
@app.route('/chat')
def chat():
    seo = get_seo_data("chat", "AI Chatbot", "Talk with our AI assistant.")
    return render_template('chatbot.html', seo=seo)

@app.route('/get_response', methods=['POST'])
def get_response():
    msg = request.json.get('message')
    if not msg:
        return jsonify({"response": "Please type a message."})
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": msg}]
        )
        reply = completion.choices[0].message.content.strip()
        return jsonify({"response": reply})
    except Exception as e:
        logging.error(f"OpenAI Error: {e}")
        return jsonify({"response": "AI service unavailable."})

# =========================
# Static Pages
# =========================
@app.route('/services')
def services():
    seo = get_seo_data("services", "Our Services", "Web development, design, and video editing services.")
    return render_template('services.html', seo=seo)

@app.route('/portfolio')
def portfolio():
    seo = get_seo_data("portfolio", "Our Portfolio", "Explore ZahidSolution projects.")
    return render_template('portfolio.html', seo=seo)

# =========================
# Admin Pages
# =========================
@app.route('/admin/login')
def admin_login():
    seo = get_seo_data("admin", "Admin Login", "Login to the admin panel.")
    return render_template('admin_login.html', seo=seo)

@app.route('/admin/portfolio')
def admin_portfolio():
    seo = get_seo_data("admin", "Admin Portfolio", "Manage portfolio items.")
    return render_template('admin_portfolio.html', seo=seo)

@app.route('/admin/dashboard')
def admin_dashboard():
    seo = get_seo_data("admin", "Admin Dashboard", "Welcome to ZahidSolution admin dashboard.")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        # Fetch stats for dashboard
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_feedback = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM newsletter")
        total_subscribers = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM blog")
        total_blogs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM portfolio")
        total_portfolio = cursor.fetchone()[0]

    except Exception as e:
        logging.error(f"Admin dashboard DB error: {e}")
        total_feedback = total_subscribers = total_blogs = total_portfolio = 0

    conn.close()

    # Pass stats to template
    return render_template(
        'admin_dashboard.html',
        seo=seo,
        total_feedback=total_feedback,
        total_subscribers=total_subscribers,
        total_blogs=total_blogs,
        total_portfolio=total_portfolio
    )

# =========================
# Run App
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
