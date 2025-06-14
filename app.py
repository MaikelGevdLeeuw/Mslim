from flask import Flask, render_template, request, redirect, session, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'geheim123'

# Gebruikers met rollen
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "user123", "role": "user"},
}

# Globale lijsten (in-memory opslag)
permits = []
assets = []
tasks = [
    {"assigned_to": "user1", "title": "Controleer noodverlichting", "status": "open"},
    {"assigned_to": "user1", "title": "Inspectie koeling A", "status": "in progress"},
]
shift_logs = {}

@app.route('/')
def index():
    if not session.get("user"):
        return redirect("/login")
    
    username = session["user"]
    role = session["role"]
    today = datetime.today().strftime("%Y-%m-%d")
    relevant_permits = permits if role == "admin" else [p for p in permits if p["engineer"] == username]
    today_permits = [p for p in relevant_permits if p["date"] == today]

    return render_template("index.html", permits=relevant_permits, today_permits=today_permits, role=role, assets=assets)

@app.route('/submit', methods=['POST'])
def submit():
    if not session.get("user"):
        return redirect("/login")

    asset_id = int(request.form['asset'])
    asset = next((a for a in assets if a['id'] == asset_id), None)

    permit = {
        'number': len(permits) + 1,
        'engineer': session.get('user'),
        'date': request.form['date'],
        'time': request.form['time'],
        'area': request.form['area'],
        'site': request.form['site'],
        'floor': request.form['floor'],
        'room': request.form['room'],
        'type': request.form['type'],
        'iso': request.form['iso'],
        'chg': request.form['chg'],
        'status': 'pending',
        'asset': asset['name'] if asset else '',
        'category': asset['category'] if asset else ''
    }
    permits.append(permit)
    return redirect('/')

@app.route('/get_assets_by_category/<category>')
def get_assets_by_category(category):
    filtered = [a for a in assets if a['category'] == category]
    return jsonify(filtered)

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
    session.clear()
    return redirect('/login')

@app.route('/home')
def home():
    if not session.get("user"):
        return redirect("/login")
    user = session["user"]
    user_tasks = [t for t in tasks if t["assigned_to"] == user]
    return render_template("home.html", tasks=user_tasks, user=user)

@app.route('/shift', methods=["GET", "POST"])
def shift():
    if not session.get("user"):
        return redirect("/login")

    user = session["user"]

    if request.method == "POST":
        data = {
            "site": request.form.get("site"),
            "date": request.form.get("date"),
            "time_on_duty": request.form.get("time_on_duty"),
            "shift": request.form.get("shift"),
            "name": request.form.get("name"),
            "equipment_issues": request.form.get("equipment_issues"),
            "major_alarms": request.form.get("major_alarms"),
            "escorts": request.form.get("escorts"),
            "pms_completed": request.form.get("pms_completed"),
            "loto": request.form.get("loto"),
            "vendors_in": request.form.get("vendors_in"),
            "vendors_out": request.form.get("vendors_out"),
            "round_timestamps": request.form.get("round_timestamps"),
            "deliveries": request.form.get("deliveries"),
            "customer_tickets": request.form.get("customer_tickets"),
            "safety": request.form.get("safety"),
            "others": request.form.get("others"),
            "time_off_duty": request.form.get("time_off_duty"),
            "hours_worked": request.form.get("hours_worked"),
            "signature": request.form.get("signature")
        }
        shift_logs[user] = data
        return redirect("/shift")

    log = shift_logs.get(user, {})
    return render_template("shift.html", log=log, user=user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

