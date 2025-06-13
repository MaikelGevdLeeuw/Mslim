from flask import Flask, render_template, request, redirect

app = Flask(__name__)

permits = []
assets = []

@app.route('/')
def index():
    return render_template('index.html', permits=permits)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    permits.append({'name': name})
    return redirect('/')

@app.route('/assets')
def asset_list():
    return render_template('assets.html', assets=assets)

@app.route('/add_asset', methods=['POST'])
def add_asset():
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
