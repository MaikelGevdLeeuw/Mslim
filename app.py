from flask import Flask, render_template, request, redirect, session, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'geheim123'

# Gebruikers
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "user123", "role": "user"},
    "user2": {"password": "user123", "role": "user"},
}

# Data-opslag
permits = []
tasks = []
shift_logs = []
handover_signed = {}

# Helpers
def is_today(date_str):
    return date_str == datetime.today().strftime('%Y-%m-%d')

def is_this_week(date_str):
    today = datetime.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return start.date() <= date.date() <= end.date()
@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')

    user = session['user']
    role = session['role']
    today = datetime.today().strftime("%Y-%m-%d")

    if role == "admin":
        return render_template("index.html", role=role, users=list(users.keys()), tasks=tasks)

    user_tasks = [t for t in tasks if t["assigned_to"] == user]
    today_tasks = [t for t in user_tasks if t["start"] <= today <= t["end"]]
    week_tasks = [t for t in user_tasks if is_this_week(t["start"])]
    today_permits = [p for p in permits if p["engineer"] == user and is_today(p["date"])]
    week_permits = [p for p in permits if p["engineer"] == user and is_this_week(p["date"])]
    notifications = [t for t in user_tasks if t["status"] != "completed" and t["end"] < today]

    return render_template("index.html",
                           role=role,
                           today_tasks=today_tasks,
                           week_tasks=week_tasks,
                           today_permits=today_permits,
                           week_permits=week_permits,
                           notifications=notifications,
                           user=user)

@app.route('/assign_task', methods=["POST"])
def assign_task():
    if session.get("role") != "admin":
        return "Unauthorized", 403

    task = {
        "assigned_to": request.form["assigned_to"],
        "title": request.form["title"],
        "start": request.form["start"],
        "end": request.form["end"],
        "status": "open"
    }
    tasks.append(task)
    return redirect('/')

@app.route('/complete_task', methods=["POST"])
def complete_task():
    index = int(request.form["index"])
    user = session["user"]
    user_tasks = [t for t in tasks if t["assigned_to"] == user]
    task = user_tasks[index]
    task["status"] = "completed"
    return redirect('/')

@app.route('/shift', methods=["GET", "POST"])
def shift():
    if 'user' not in session:
        return redirect('/login')
    user = session['user']

    if request.method == "POST":
        data = {
            "user": user,
            "date": request.form["date"],
            "handover": request.form["handover"],
            "accepted_by": "",
            "issues": request.form["issues"]
        }
        shift_logs.append(data)
        handover_signed[user] = True
        return redirect('/shift')

    # Als handover al is gedaan, laat dan de laatste log zien voor overname
    handovers = [log for log in shift_logs if log["user"] == user]
    last = handovers[-1] if handovers else None
    return render_template("shift.html", user=user, last=last, signed=handover_signed.get(user, False))

@app.route('/accept_shift', methods=["POST"])
def accept_shift():
    accepter = session['user']
    for log in shift_logs:
        if not log["accepted_by"]:
            log["accepted_by"] = accepter
            break
    return redirect('/shift')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user['password'] == password:
            session['user'] = username
            session['role'] = user['role']
            return redirect('/')
        return "Foutieve login."
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
