from flask import Flask, render_template, request

app = Flask(__name__)

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# Services Route
@app.route('/services')
def services():
    return render_template('services.html')

# Portfolio Route
@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

# Contact Route
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Feedback Route (GET & POST)
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        feedback_text = request.form['feedback']
        # For now, we'll just print the feedback in console
        print(f"Feedback from {name}: {feedback_text}")
        return "Thank you for your feedback!"
    return render_template('feedback.html')

# Run Server
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
