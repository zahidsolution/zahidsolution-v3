from flask import Flask, render_template, request, redirect, session, url_for, flash, Response, jsonify
import sqlite3
import os
import re
from werkzeug.utils import secure_filename
from slugify import slugify  # pip install python-slugify

app = Flask(__name__)
app.secret_key = "zahid_secret_key"

# =========================
# Upload Folder
# =========================
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# =========================
# Database initialize
# =========================
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            message TEXT,
            reply TEXT
        )
    ''')

    # Portfolio table
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

    # Newsletter table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS newsletter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT
        )
    ''')

    # Blog table (NEW)
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
        },
        "services": {
            "title": "Our Services - ZahidSolution",
            "description": "Explore our web development, graphic design, and video editing services designed to elevate your brand.",
            "keywords": "services, web design, video editing, branding, ZahidSolution"
        },
        "portfolio": {
            "title": "Our Portfolio - ZahidSolution",
            "description": "Check out our portfolio showcasing web development, design, and editing projects.",
            "keywords": "portfolio, projects, ZahidSolution, web development, design"
        },
        "contact": {
            "title": "Contact Us - ZahidSolution",
            "description": "Get in touch with ZahidSolution for your web, design, and editing needs. Contact via WhatsApp, phone, or email.",
            "keywords": "contact, ZahidSolution, support, web services, WhatsApp"
        },
        "feedback": {
            "title": "Feedback - ZahidSolution",
            "description": "Share your feedback and help us improve our services at ZahidSolution.",
            "keywords": "feedback, review, ZahidSolution"
        },
        "admin": {
            "title": "Admin Login - ZahidSolution",
            "description": "Admin panel for ZahidSolution to manage portfolio and feedback.",
            "keywords": "admin login, ZahidSolution dashboard"
        }
    }
    if dynamic_title:
        seo["dynamic"] = {
            "title": dynamic_title,
            "description": dynamic_description or "",
            "keywords": dynamic_title
        }
        return seo["dynamic"]
    return seo.get(page_name, seo["home"])

# =========================
# Public Routes
# =========================
@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Portfolio projects
    cursor.execute('SELECT * FROM portfolio ORDER BY id DESC LIMIT 3')
    recent_projects = cursor.fetchall()

    # Fetch latest blog posts (NEW)
    cursor.execute('SELECT id, title, slug, substr(content, 1, 120) FROM blog ORDER BY created_at DESC LIMIT 3')
    blog_posts = cursor.fetchall()

    # Counters
    project_count = cursor.execute('SELECT COUNT(*) FROM portfolio').fetchone()[0]
    feedback_count = cursor.execute('SELECT COUNT(*) FROM feedback').fetchone()[0]

    conn.close()

    seo = get_seo_data("home")
    return render_template(
        'index.html',
        projects=recent_projects,
        blog_posts=blog_posts,  # NEW
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
    if 'admin' not in session:
        return redirect('/admin')

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

@app.route('/admin/blog/delete/<int:blog_id>')
def delete_blog(blog_id):
    if 'admin' not in session:
        return redirect('/admin')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM blog WHERE id=?', (blog_id,))
    conn.commit()
    conn.close()

    flash("Blog deleted successfully!", "success")
    return redirect('/admin/blog')

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

@app.route('/api/blog')
def api_blog():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, content, slug FROM blog ORDER BY id DESC LIMIT 3')
    blogs = cursor.fetchall()
    conn.close()

    return {"blogs": [{"id": b[0], "title": b[1], "content": b[2], "slug": b[3]} for b in blogs]}

# =========================
# Live Chatbot API (Optional)
# =========================
@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    data = request.get_json()
    user_message = data.get("message", "").lower()

    if "hello" in user_message or "hi" in user_message:
        reply = "Hello! How can I help you with web development or design today?"
    elif "price" in user_message:
        reply = "Our pricing starts from $99 for basic websites. Would you like to see the full pricing plans?"
    elif "contact" in user_message:
        reply = "You can contact us at zahidsolutions360@gmail.com or via WhatsApp at +923000079078."
    else:
        reply = "I'm not sure about that, but our team will get back to you soon!"

    return {"reply": reply}
