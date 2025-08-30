from flask import Flask, render_template, request, redirect, session, flash, jsonify
import sqlite3
import os
from slugify import slugify
import openai
import logging
from dotenv import load_dotenv

load_dotenv()  # Load .env variables if present

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
# Logging Setup
# =========================
logging.basicConfig(level=logging.INFO)

# =========================
# Database Initialization
# =========================
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Updated feedback table with rating and submitted_at
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
def get_seo_data(page_name, dynamic_title=None, dynamic_description=None):
    seo = {
        "home": {
            "title": "ZahidSolution - Web Development, Design & Editing",
            "description": "Professional web development, graphic design, and video editing services tailored for your business success.",
            "keywords": "web development, graphic design, video editing, ZahidSolution, portfolio, Pakistan"
        }
    }
    if dynamic_title:
        return {
            "title": dynamic_title,
            "description": dynamic_description or "",
            "keywords": dynamic_title
        }
    return seo.get(page_name, seo["home"])

# =========================
# Routes
# =========================
@app.route('/')
def home_page():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, message, rating FROM feedback ORDER BY id DESC LIMIT 5")  # show latest 5
    feedbacks = cursor.fetchall()
    conn.close()

    seo = get_seo_data("home", "Welcome to ZahidSolution", "Professional Web, Video, and Graphic Solutions")
    return render_template('index.html', seo=seo, feedbacks=feedbacks)

# Admin blog
@app.route('/admin/blog', methods=['GET', 'POST'])
def admin_blog():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        slug = slugify(title)
        cursor.execute('INSERT INTO blog (title, content, slug) VALUES (?, ?, ?)', (title, content, slug))
        conn.commit()
    cursor.execute('SELECT * FROM blog ORDER BY id DESC')
    blog_posts = cursor.fetchall()
    conn.close()
    return render_template('admin_blog.html', blog_posts=blog_posts)

@app.route('/blog/<slug>')
def blog_detail(slug):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blog WHERE slug=?', (slug,))
    blog_post = cursor.fetchone()
    conn.close()
    if not blog_post:
        return redirect('/')
    seo = get_seo_data("dynamic", blog_post[1], blog_post[2][:160])
    return render_template('blog_detail.html', blog=blog_post, seo=seo)

@app.route('/newsletter', methods=['POST'])
def newsletter():
    email = request.form['email']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO newsletter (email) VALUES (?)', (email,))
        conn.commit()
        flash("Thanks for subscribing to our newsletter!", "success")
    except sqlite3.IntegrityError:
        flash("You are already subscribed!", "info")
    conn.close()
    return redirect('/')

# =========================
# Feedback Route (Fixed)
# =========================
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name') or 'Anonymous'
        email = request.form.get('email')
        message = request.form.get('message')
        rating = int(request.form.get('rating', 0))
        honeypot = request.form.get('honeypot')

        # Spam check
        if honeypot:
            return jsonify({"error": "Spam detected!"})

        if not email or not message:
            return jsonify({"error": "Email and message are required."})

        try:
            cursor.execute(
                "INSERT INTO feedback (name, email, message, rating, submitted_at) VALUES (?, ?, ?, ?, datetime('now'))",
                (name, email, message, rating)
            )
            conn.commit()
            return jsonify({"success": True, "name": name, "message": message, "rating": rating, "date": "Just now"})
        except Exception as e:
            print("DB Error:", e)
            return jsonify({"error": "Database error, try again."})

    # GET request
    cursor.execute("SELECT name, email, message, rating, submitted_at FROM feedback ORDER BY submitted_at DESC")
    feedbacks = cursor.fetchall()
    conn.close()

    seo = get_seo_data("feedback", "Customer Feedback", "Read what our clients say about ZahidSolution services.")
    return render_template('feedback.html', seo=seo, feedbacks=feedbacks)
@app.route('/feedback', methods=['GET', 'POST'])
def feedback_page():
    seo = get_seo_data("feedback", "Customer Feedback", "Read what our clients say about ZahidSolution services.")

    if request.method == 'POST':
        try:
            name = request.form.get('name') or 'Anonymous'
            email = request.form.get('email')
            message = request.form.get('message')
            rating = int(request.form.get('rating') or 0)
            honeypot = request.form.get('honeypot')

            # Spam check
            if honeypot:
                return jsonify({"error": "Spam detected."})

            if not email or not message:
                return jsonify({"error": "Email and message are required."})

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO feedback (name, email, message, reply) VALUES (?, ?, ?, ?)''',
                (name, email, message, "")
            )
            conn.commit()

            # Fetch inserted feedback date
            cursor.execute('SELECT datetime("now")')
            date = cursor.fetchone()[0]

            conn.close()

            return jsonify({
                "success": True,
                "name": name,
                "message": message,
                "rating": rating,
                "date": date
            })

        except Exception as e:
            print("Feedback Error:", str(e))
            return jsonify({"error": "Failed to submit feedback."})

    # GET request
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, email, message, reply, datetime('now') as date FROM feedback ORDER BY id DESC")
        feedbacks = cursor.fetchall()
        conn.close()
    except Exception as e:
        print("Fetch feedback error:", str(e))
        feedbacks = []

    return render_template('feedback.html', seo=seo, feedbacks=feedbacks)
# =========================
# Chatbot
# =========================
@app.route('/chat')
def chatbot():
    seo = get_seo_data("chat", "AI Chatbot", "Talk with our AI-powered assistant.")
    return render_template('chatbot.html', seo=seo)

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"response": "Please type a message."})
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = completion.choices[0].message.content.strip()
        return jsonify({"response": reply})
    except Exception as e:
        logging.error(f"OpenAI Error: {e}")
        return jsonify({"response": "Sorry, I'm having trouble reaching the AI service."})

# =========================
# Static Pages
# =========================
@app.route('/services')
def services():
    seo = get_seo_data("services", "Our Services", "Explore ZahidSolution services including web development, design, and video editing.")
    return render_template('services.html', seo=seo)

@app.route('/portfolio')
def portfolio():
    seo = get_seo_data("portfolio", "Our Portfolio", "See ZahidSolution’s portfolio of web development, graphic design, and video editing projects.")
    return render_template('portfolio.html', seo=seo)

# =========================
# Admin Pages
# =========================
@app.route('/admin/login')
def admin_login():
    seo = get_seo_data("admin", "Admin Login", "Login to ZahidSolution admin panel.")
    return render_template('admin_login.html', seo=seo)

@app.route('/admin/portfolio')
def admin_portfolio():
    seo = get_seo_data("admin", "Admin Portfolio", "Manage ZahidSolution portfolio items.")
    return render_template('admin_portfolio.html', seo=seo)

@app.route('/admin/dashboard')
def admin_dashboard():
    seo = get_seo_data("admin", "Admin Dashboard", "Welcome to ZahidSolution admin dashboard.")
    return render_template('admin_dashboard.html', seo=seo)

# =========================
# Run App
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
