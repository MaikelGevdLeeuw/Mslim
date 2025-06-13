from flask import Flask, render_template, request, redirect, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'geheim123'  # gebruik een sterke secret key in productie

# Gebruikers
users = {
    "admin": "test123"
}

# Tijdelijke opslag
permits = []
assets = []

@app.route('/')
def index():
    if not session.get("user"):
        return redirect("/login")
    return render_template('index.html', permits=permits)

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
        'chg': request.form['chg']
    }
    permits.append(permit)
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            session['user'] = username
            return redirect('/')
        return "Foutieve login. Probeer opnieuw."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/assets')
def asset_list():
    if not session.get("user"):
        return redirect("/login")
    return render_template('assets.html', assets=assets)

@app.route('/add_asset', methods=['POST'])
def add_asset():
    if not session.get("user"):
        return redirect("/login")

    asset = {
        'id': len(assets) + 1,
        'name': request.form['name'],
        'type': request.form['type'],
        'location': request.form['location'],
        'serial': request.form['serial']
    }
    assets.append(asset)
    return redirect('/assets')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
