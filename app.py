from flask import Flask, render_template, request, redirect, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'geheim123'

users = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "user123", "role": "user"},
}

permits = []
assets = []

@app.route('/')
def index():
    if not session.get("user"):
        return redirect("/login")

    role = session.get("role")
    username = session.get("user")
    today = datetime.today().strftime("%Y-%m-%d")

    if role == "admin":
        today_permits = [p for p in permits if p.get("date") == today]
        return render_template("index.html", permits=permits, today_permits=today_permits, role=role)

    else:
        user_permits = [p for p in permits if p.get("engineer") == username]
        today_permits = [p for p in user_permits if p.get("date") == today]
        return render_template("index.html", permits=user_permits, today_permits=today_permits, role=role)

@app.route('/submit', methods=['POST'])
def submit():
    if not session.get("user"):
        return redirect("/login")

    permit = {
        'number': len(permits) + 1,
        'engineer': session.get('user'),
        'date': request.form['date'],
        'time': request.form['time'],
        'area': request.form['area'],
        'type': request.form['type'],
        'iso': request.form['iso'],
        'chg': request.form['chg'],
        'status': 'pending'
    }
    permits.append(permit)
    return redirect('/')

@app.route('/update_status/<int:number>', methods=['POST'])
def update_status(number):
    if session.get("role") != "admin":
        return "Geen toegang", 403

    new_status = request.form.get("status")
    for p in permits:
        if p["number"] == number:
            p["status"] = new_status
            break
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)

        if user and user['password'] == password:
            session['user'] = username
            session['role'] = user['role']
            return redirect('/')
        return "Foutieve login. Probeer opnieuw."

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
