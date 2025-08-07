from flask import Flask, render_template, request, redirect, session, flash, jsonify
import sqlite3
import os
from slugify import slugify
import openai
import logging

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
# Logging Setup (optional but useful on Render)
# =========================
logging.basicConfig(level=logging.INFO)

# =========================
# Database initialize
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
            reply TEXT
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
# SEO UTILITIES
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
# Public Routes
# =========================
@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM portfolio ORDER BY id DESC LIMIT 3')
    recent_projects = cursor.fetchall()

    cursor.execute('SELECT id, title, slug, substr(content, 1, 120) FROM blog ORDER BY created_at DESC LIMIT 3')
    blog_posts = cursor.fetchall()

    project_count = cursor.execute('SELECT COUNT(*) FROM portfolio').fetchone()[0]
    feedback_count = cursor.execute('SELECT COUNT(*) FROM feedback').fetchone()[0]

    conn.close()

    seo = get_seo_data("home")
    return render_template(
        'index.html',
        projects=recent_projects,
        blog_posts=blog_posts,
        seo=seo,
        project_count=project_count,
        feedback_count=feedback_count,
        years_experience=3,
        hours_support=24
    )

# =========================
# Blog Routes
# =========================
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

# =========================
# Newsletter Route
# =========================
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
# Feedback Route
# =========================
@app.route('/contact', methods=['POST'])
def contact():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO feedback (name, email, message) VALUES (?, ?, ?)', (name, email, message))
    conn.commit()
    conn.close()

    flash("Your message has been sent successfully!", "success")
    return redirect('/')

# =========================
# Chatbot Page & API
# =========================
@app.route('/chat')
def chatbot():
    seo = get_seo_data("chat", "AI Chatbot", "Talk with our AI-powered assistant.")
    return render_template('chatbot.html', seo=seo)

@app.route('/get-response', methods=['POST'])
def get_response():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"response": "Please enter a message."})

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = completion.choices[0].message.content.strip()
        return jsonify({"response": reply})
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return jsonify({"response": "Sorry, something went wrong connecting to the AI."})

# =========================
# Run the App
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
