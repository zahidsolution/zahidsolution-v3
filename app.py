from flask import Flask, render_template, request, redirect, session, url_for, flash, Response
import sqlite3
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "zahid_secret_key"

# =========================
# Upload Folder (for images/videos)
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
            message TEXT
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

    # Add columns if missing
    try:
        cursor.execute("ALTER TABLE portfolio ADD COLUMN media_type TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE portfolio ADD COLUMN category TEXT")
    except:
        pass

    conn.commit()
    conn.close()

init_db()

# =========================
# SEO UTILITIES
# =========================
def get_seo_data(page_name):
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
    conn.close()

    seo = get_seo_data("home")
    return render_template('index.html', recent_projects=recent_projects, seo=seo)

@app.route('/services')
def services():
    seo = get_seo_data("services")
    return render_template('services.html', seo=seo)

@app.route('/portfolio')
def portfolio_page():
    category = request.args.get('category', 'all')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if category == 'all':
        cursor.execute('SELECT * FROM portfolio')
    else:
        cursor.execute('SELECT * FROM portfolio WHERE category = ?', (category,))

    projects = cursor.fetchall()
    conn.close()

    seo = get_seo_data("portfolio")
    return render_template('portfolio.html', projects=projects, selected_category=category, seo=seo)

# =========================
# Contact Page (Enhanced with WhatsApp, Call, Email Buttons)
# =========================
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    seo = get_seo_data("contact")

    contact_info = {
        "phone": "+923000079078",
        "phone_local": "03000079078",
        "email": "zahidsolutions360@gmail.com",
        "whatsapp": "+923000079078"
    }

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            flash("All fields are required.", "error")
            return redirect('/contact')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Please enter a valid email address.", "error")
            return redirect('/contact')

        flash("Thank you for contacting us! We will get back to you soon.", "success")
        return redirect('/contact')

    return render_template('contact.html', seo=seo, contact_info=contact_info)

# =========================
# Feedback
# =========================
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    seo = get_seo_data("feedback")
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Please enter a valid email address.", "error")
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM feedback')
            feedbacks = cursor.fetchall()
            conn.close()
            return render_template('feedback.html', feedbacks=feedbacks, seo=seo)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO feedback (name, email, message) VALUES (?, ?, ?)',
                       (name, email, message))
        conn.commit()
        conn.close()

        flash("Thank you for your feedback!", "success")
        return redirect('/feedback')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM feedback')
    feedbacks = cursor.fetchall()
    conn.close()

    return render_template('feedback.html', feedbacks=feedbacks, seo=seo)

# =========================
# Admin Login
# =========================
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    seo = get_seo_data("admin")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "1234":
            session['admin'] = True
            return redirect('/admin/dashboard')
    return render_template('admin_login.html', seo=seo)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/admin')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM feedback')
    feedbacks = cursor.fetchall()

    cursor.execute('SELECT * FROM portfolio')
    projects = cursor.fetchall()

    conn.close()
    return render_template('admin_dashboard.html', feedbacks=feedbacks, projects=projects)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin')

# =========================
# Portfolio Management (Admin)
# =========================
@app.route('/admin/portfolio', methods=['POST'])
def add_portfolio():
    if 'admin' not in session:
        return redirect('/admin')

    title = request.form['title']
    description = request.form['description']
    category = request.form['category']
    file = request.files['file']

    file_name = None
    media_type = "image"

    if file and file.filename.strip() != '':
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()

        if file_ext in ['.mp4', '.mov', '.avi', '.webm']:
            media_type = "video"
        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            media_type = "image"
        else:
            flash("Unsupported file type!", "error")
            return redirect('/admin/dashboard')

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_name = filename

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO portfolio (title, description, file, media_type, category) VALUES (?, ?, ?, ?, ?)',
                   (title, description, file_name, media_type, category))
    conn.commit()
    conn.close()

    return redirect('/admin/dashboard')

@app.route('/admin/portfolio/delete/<int:project_id>')
def delete_portfolio(project_id):
    if 'admin' not in session:
        return redirect('/admin')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT file FROM portfolio WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    if project and project[0]:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], project[0])
        if os.path.exists(file_path):
            os.remove(file_path)

    cursor.execute('DELETE FROM portfolio WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()

    return redirect('/admin/dashboard')

# =========================
# SEO: Sitemap and Robots
# =========================
@app.route('/sitemap.xml')
def sitemap():
    pages = [
        {'loc': url_for('home', _external=True)},
        {'loc': url_for('services', _external=True)},
        {'loc': url_for('portfolio_page', _external=True)},
        {'loc': url_for('contact', _external=True)},
        {'loc': url_for('feedback', _external=True)}
    ]
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    return Response(sitemap_xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    return Response("User-Agent: *\nAllow: /\nSitemap: " + url_for('sitemap', _external=True), mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
