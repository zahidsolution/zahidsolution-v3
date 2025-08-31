from flask import Flask, render_template, request, redirect, flash, session, url_for
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
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'mkv'}  # Images + Videos

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    
    # Create feedback table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,           -- Added phone column
            message TEXT,
            rating INTEGER DEFAULT 0,
            reply TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            email TEXT UNIQUE
        )
    ''')

    # Blog table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            slug TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Extra check: add phone column if missing
    cursor.execute("PRAGMA table_info(feedback)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'phone' not in columns:
        cursor.execute("ALTER TABLE feedback ADD COLUMN phone TEXT")

    conn.commit()
    conn.close()

init_db()

# =========================
# 
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
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    seo = get_seo_data(
        "contact",
        "Contact Us - ZahidSolution",
        "Get in touch with ZahidSolution for web development, graphic design, and video editing services."
    )

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Handle feedback form submission
    if request.method == 'POST':
        name = request.form.get('name', 'Anonymous')
        email = request.form.get('email')
        phone = request.form.get('phone', '')
        message = request.form.get('message')
        rating = int(request.form.get('rating', 0))

        if not email or not message:
            flash("Email and message are required!", "danger")
        else:
            cursor.execute(
                "INSERT INTO feedback (name, email, phone, message, rating, submitted_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
                (name, email, phone, message, rating)
            )
            conn.commit()
            flash("Thank you for your feedback!", "success")

    # Fetch latest 5 feedbacks
    cursor.execute("SELECT name, email, phone, message, rating, submitted_at FROM feedback ORDER BY id DESC LIMIT 5")
    feedbacks = cursor.fetchall()
    conn.close()

    # AI greeting text
    ai_greeting = (
        "Welcome to ZahidSolution! Zahid Hussain is an exceptionally talented developer, "
        "designer, and video editor. You can contact him directly on WhatsApp for a quick reply. "
        "Here are some topics you might be interested in:"
    )

    # WhatsApp number
    whatsapp_number = "+923000079078"  # Replace with actual number
    whatsapp_link = https://wa.me/923000079078?text=Hi%20there!%20I%27m%20excited%20to%20learn%20about%20Zahid%20Solution%27s%20services.%20Could%20you%20please%20share%20details%20on%20website%20development%2C%20graphic%20design%2C%20or%20video%20editing%20services%3F

    # Suggested topics (dynamic)
    ai_suggestions = ["Services", "Pricing", "Portfolio", "Video Editing", "Graphic Design", "Web Development", "Contact"]

    return render_template(
        'contact.html',
        seo=seo,
        feedbacks=feedbacks,
        ai_greeting=ai_greeting,
        whatsapp_link=whatsapp_link,
        ai_suggestions=ai_suggestions
    )


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
        # System prompt to guide AI for ZahidSolution info
        system_prompt = """
        You are ZahidSolution's virtual assistant. Answer questions about:
        - ZahidSolution services (Web Development, Video Editing, Graphic Designing)
        - Pricing
        - Website features
        - Contact info
        - About Zahid Hussain and ZahidSolution
        Provide short, friendly, clear answers.
        Also suggest relevant topics the user can ask about, like:
        'Services', 'Pricing', 'Contact', 'About Zahid Hussain', 'Portfolio', 'Video Editing Features'.
        """
        
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg}
            ],
            temperature=0.8,  # Higher temp = more varied responses
            max_tokens=300
        )

        reply_text = completion.choices[0].message.content.strip()

        # Optional: predefined suggestions
        suggestions = [
            "Services",
            "Pricing",
            "Contact",
            "About Zahid Hussain",
            "Portfolio",
            "Video Editing Features",
            "Website Features"
        ]

        return jsonify({"response": reply_text, "suggestions": suggestions})

    except Exception as e:
        logging.error(f"OpenAI Error: {e}")
        return jsonify({"response": "AI service unavailable.", "suggestions": []})


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
app.secret_key = "9e1f3c4a82b6d7f1aa4c58e2d0b9c3f7"


#=====================

#Admin Login

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    seo = get_seo_data("admin", "Admin Login", "Login to the admin panel.")

    if request.method == 'POST':  
        username = request.form.get('username')  
        password = request.form.get('password')  

        # Example: check credentials (replace with DB check)  
        if username == "admin" and password == "1234":  
            session['admin_logged_in'] = True  
            flash("Login successful!", "success")  
            return redirect(url_for('admin_dashboard'))  
        else:  
            error = "Invalid username or password"  
            return render_template('admin_login.html', seo=seo, error=error)  

    return render_template('admin_login.html', seo=seo)

#=====================

#Admin Dashboard
# =====================
# Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):   # Security check
        return redirect(url_for('admin_login'))

    seo = get_seo_data("admin", "Admin Dashboard", "Welcome to ZahidSolution admin dashboard.")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        # Stats
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_feedback = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM newsletter")
        total_subscribers = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM blog")
        total_blogs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM portfolio")
        total_portfolio = cursor.fetchone()[0]

        # All feedbacks
        cursor.execute("SELECT id, name, email, message, rating, submitted_at FROM feedback ORDER BY id DESC")
        feedbacks = cursor.fetchall()

        # All projects
        cursor.execute("SELECT id, title, description, file, media_type, category FROM portfolio ORDER BY id DESC")
        projects = cursor.fetchall()

    except Exception as e:
        logging.error(f"Admin dashboard DB error: {e}")
        total_feedback = total_subscribers = total_blogs = total_portfolio = 0
        feedbacks = []
        projects = []

    conn.close()

    return render_template(
        'admin_dashboard.html',
        seo=seo,
        total_feedback=total_feedback,
        total_subscribers=total_subscribers,
        total_blogs=total_blogs,
        total_portfolio=total_portfolio,
        feedbacks=feedbacks,
        projects=projects
    )


# =====================
# Admin Logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('admin_login'))


# =========================
# Add Portfolio Project
# =========================
@app.route('/admin/portfolio', methods=['POST'])
def add_portfolio():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    title = request.form['title']
    category = request.form['category']
    description = request.form['description']
    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = slugify(title) + "_" + file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        media_type = 'video' if file.filename.rsplit('.', 1)[1].lower() in {'mp4','mov','avi','mkv'} else 'image'

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO portfolio (title, description, file, media_type, category) VALUES (?, ?, ?, ?, ?)",
            (title, description, filename, media_type, category)
        )
        conn.commit()
        conn.close()

        flash("Project added successfully!", "success")
    else:
        flash("Invalid file type!", "danger")

    return redirect(url_for('admin_dashboard'))
    

    
# =========================
# Delete Portfolio Project
# =========================
@app.route('/admin/portfolio/delete/<int:project_id>')
def delete_portfolio(project_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        # Delete file
        cursor.execute("SELECT file FROM portfolio WHERE id=?", (project_id,))
        file_row = cursor.fetchone()
        if file_row:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_row[0])
            if os.path.exists(file_path):
                os.remove(file_path)
        # Delete from DB
        cursor.execute("DELETE FROM portfolio WHERE id=?", (project_id,))
        conn.commit()
        flash("Project deleted successfully!", "success")
    except Exception as e:
        logging.error(f"Delete portfolio error: {e}")
        flash("Failed to delete project.", "danger")
    finally:
        conn.close()
    return redirect('/admin/dashboard')


# =========================
# Delete Feedback
# =========================
@app.route('/admin/feedback/delete/<int:feedback_id>')
def delete_feedback(feedback_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM feedback WHERE id=?", (feedback_id,))
        conn.commit()
        flash("Feedback deleted successfully!", "success")
    except Exception as e:
        logging.error(f"Delete feedback error: {e}")
        flash("Failed to delete feedback.", "danger")
    finally:
        conn.close()
    return redirect('/admin/dashboard')
    


# =========================
# Run App
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
