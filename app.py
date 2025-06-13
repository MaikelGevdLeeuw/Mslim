from flask import Flask, render_template, request, redirect, session, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'geheim123'

users = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "user123", "role": "user"},
}

permits = []
assets = [
    {
        'id': 1,
        'name': 'Koeling A',
        'type': 'HVAC',
        'category': 'Cooling',
        'location': 'Room 1',
        'floor': '1',
        'site': 'AMS1',
        'serial': 'ABC123',
        'vendor': 'CoolTech BV',
        'vendor_phone': '+31 20 123 4567',
        'vendor_email': 'service@cooltech.nl',
        'install_date': '2023-01-10',
        'last_maintenance': '2024-06-01',
        'maintenance_due': '2025-06-01',
        'maintenance_interval': '12 maanden',
        'vendor_contract_active': True,
        'active': True,
        'iso': 'ISO-50001',
        'notes': 'Zit aangesloten op N+1 koelsysteem'
    },
    {
        'id': 2,
        'name': 'PDU 5',
        'type': 'Power',
        'category': 'Power',
        'location': 'Room 2',
        'floor': '2',
        'site': 'AMS1',
        'serial': 'XYZ456',
        'vendor': 'PowerFlow BV',
        'vendor_phone': '+31 10 987 6543',
        'vendor_email': 'support@powerflow.nl',
        'install_date': '2022-09-15',
        'last_maintenance': '2024-03-20',
        'maintenance_due': '2025-03-20',
        'maintenance_interval': '12 maanden',
        'vendor_contract_active': False,
        'active': False,
        'iso': 'ISO-9001',
        'notes': 'PDU buiten gebruik gesteld wegens lekkage'
    }
]

@app.route('/')
def index():
    if not session.get("user"):
        return redirect("/login")

    role = session.get("role")
    username = session.get("user")
    today = datetime.today().strftime("%Y-%m-%d")

    if role == "admin":
        today_permits = [p for p in permits if p.get("date") == today]
        return render_template("index.html", permits=permits, today_permits=today_permits, role=role, assets=assets)

    user_permits = [p for p in permits if p.get("engineer") == username]
    today_permits = [p for p in user_permits if p.get("date") == today]
    return render_template("index.html", permits=user_permits, today_permits=today_permits, role=role, assets=assets)

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
    session.pop('user', None)
    session.pop('role', None)
    return redirect('/login')

@app.route('/assets')
def show_assets():
    if not session.get("user"):
        return redirect("/login")
    return render_template("assets.html", assets=assets, role=session.get("role"))
