from flask import Flask, render_template, request, redirect, session, url_for, flash
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

    # Portfolio table with category & media_type
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

    conn.commit()
    conn.close()

init_db()

# =========================
# Public Routes
# =========================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio_page():
    category = request.args.get('category', 'all')  # filter by category if selected
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if category == 'all':
        cursor.execute('SELECT * FROM portfolio')
    else:
        cursor.execute('SELECT * FROM portfolio WHERE category = ?', (category,))

    projects = cursor.fetchall()
    conn.close()
    return render_template('portfolio.html', projects=projects, selected_category=category)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Please enter a valid email address.", "error")
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM feedback')
            feedbacks = cursor.fetchall()
            conn.close()
            return render_template('feedback.html', feedbacks=feedbacks)

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

    return render_template('feedback.html', feedbacks=feedbacks)

# =========================
# Admin Login
# =========================
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "1234":  # Simple login
            session['admin'] = True
            return redirect('/admin/dashboard')
    return render_template('admin_login.html')

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

    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()

        if file_ext in ['.mp4', '.mov', '.avi']:
            media_type = "video"
        else:
            media_type = "image"

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

    # delete file from folder
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
