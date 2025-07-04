from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        message = request.form['message']
        with open("feedback.txt", "a", encoding='utf-8') as f:
            f.write(f"{name} said: {message}\n")
        return redirect('/')
    return render_template('feedback.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
