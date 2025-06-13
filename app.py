from flask import Flask, render_template, request, redirect, session
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
        'area': asset['location'] if asset else '',
        'type': request.form['type'],
        'iso': request.form['iso'],
        'chg': request.form['chg'],
        'status': 'pending',
        'asset': asset['name'] if asset else '',
        'category': asset['category'] if asset else ''
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

@app.route('/assets')
def show_assets():
    if not session.get("user"):
        return redirect("/login")

    return render_template("assets.html", assets=assets, role=session.get("role"))

@app.route('/asset/add', methods=['GET', 'POST'])
def add_asset():
    if session.get("role") != "admin":
        return "Geen toegang", 403

    if request.method == 'POST':
        new_id = max([a['id'] for a in assets]) + 1 if assets else 1
        new_asset = {
            'id': new_id,
            'name': request.form['name'],
            'type': request.form['type'],
            'category': request.form['category'],
            'location': request.form['location'],
            'floor': request.form['floor'],
            'site': request.form['site'],
            'serial': request.form['serial'],
            'vendor': request.form['vendor'],
            'vendor_phone': request.form['vendor_phone'],
            'vendor_email': request.form['vendor_email'],
            'install_date': request.form['install_date'],
            'last_maintenance': request.form['last_maintenance'],
            'maintenance_due': request.form['maintenance_due'],
            'maintenance_interval': request.form['maintenance_interval'],
            'vendor_contract_active': request.form.get('vendor_contract_active') == 'on',
            'active': request.form.get('active') == 'on',
            'iso': request.form['iso'],
            'notes': request.form['notes']
        }
        assets.append(new_asset)
        return redirect('/assets')

    return render_template("add_asset.html")

@app.route('/asset/edit/<int:asset_id>', methods=['GET', 'POST'])
def edit_asset(asset_id):
    if session.get("role") != "admin":
        return "Geen toegang", 403

    asset = next((a for a in assets if a["id"] == asset_id), None)
    if not asset:
        return "Asset niet gevonden", 404

    if request.method == 'POST':
        asset.update({
            'name': request.form['name'],
            'type': request.form['type'],
            'category': request.form['category'],
            'location': request.form['location'],
            'floor': request.form['floor'],
            'site': request.form['site'],
            'serial': request.form['serial'],
            'vendor': request.form['vendor'],
            'vendor_phone': request.form['vendor_phone'],
            'vendor_email': request.form['vendor_email'],
            'install_date': request.form['install_date'],
            'last_maintenance': request.form['last_maintenance'],
            'maintenance_due': request.form['maintenance_due'],
            'maintenance_interval': request.form['maintenance_interval'],
            'vendor_contract_active': request.form.get('vendor_contract_active') == 'on',
            'active': request.form.get('active') == 'on',
            'iso': request.form['iso'],
            'notes': request.form['notes']
        })
        return redirect('/assets')

    return render_template("edit_asset.html", asset=asset)

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
