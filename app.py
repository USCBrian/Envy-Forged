import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, request, jsonify, redirect, url_for
from core.database import get_db, init_db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'envy-forged-dev')
ADMIN_KEY = os.environ.get('ADMIN_KEY', 'envy-admin-2025')

CONSTRUCTION_LABELS = {
    'one-piece': 'One-Piece Forged',
    'two-piece': 'Two-Piece Forged',
    'three-piece': 'Three-Piece Forged',
    'beadlock': 'Racing Beadlock',
    'htype': 'H-Type Off-Road',
    'carbon': 'Carbon Fiber',
}

FITMENT_TYPES = ['OEM', 'Tuck', 'Flush', 'Poke']

@app.route('/')
def index():
    db = get_db()
    featured = db.execute("SELECT * FROM wheels WHERE popular=1 ORDER BY sort_order LIMIT 8").fetchall()
    db.close()
    return render_template('index.html', featured=featured, labels=CONSTRUCTION_LABELS)

@app.route('/catalog')
def catalog():
    construction = request.args.get('construction', 'all')
    db = get_db()
    if construction == 'all':
        wheels = db.execute("SELECT * FROM wheels ORDER BY sort_order").fetchall()
    else:
        wheels = db.execute("SELECT * FROM wheels WHERE construction=? ORDER BY sort_order", (construction,)).fetchall()
    db.close()
    return render_template('catalog.html', wheels=wheels, active=construction, labels=CONSTRUCTION_LABELS)

@app.route('/wheel/<sku>')
def wheel_detail(sku):
    db = get_db()
    wheel = db.execute("SELECT * FROM wheels WHERE sku=?", (sku,)).fetchone()
    if not wheel:
        return redirect(url_for('catalog'))
    finishes = db.execute("SELECT * FROM finishes ORDER BY tier, name").fetchall()
    pricing = db.execute("SELECT * FROM pricing WHERE construction=? ORDER BY size_inch, finish_tier", (wheel['construction'],)).fetchall()
    db.close()
    return render_template('wheel_detail.html', wheel=wheel, finishes=finishes,
                           pricing=pricing, fitment_types=FITMENT_TYPES,
                           label=CONSTRUCTION_LABELS.get(wheel['construction'], wheel['construction']))

@app.route('/quote', methods=['GET', 'POST'])
def quote():
    db = get_db()
    if request.method == 'POST':
        d = request.form
        db.execute("""INSERT INTO quotes(name,email,phone,vehicle,wheel_sku,size_inch,finish,qty,fitment,notes)
                      VALUES(?,?,?,?,?,?,?,?,?,?)""",
                   (d.get('name'), d.get('email'), d.get('phone'), d.get('vehicle'),
                    d.get('wheel_sku'), d.get('size_inch'), d.get('finish'),
                    d.get('qty',4), d.get('fitment'), d.get('notes')))
        db.commit()
        db.close()
        return render_template('quote_confirm.html')
    wheels = db.execute("SELECT sku, name, construction FROM wheels ORDER BY sort_order").fetchall()
    finishes = db.execute("SELECT * FROM finishes ORDER BY tier, name").fetchall()
    db.close()
    return render_template('quote.html', wheels=wheels, finishes=finishes,
                           fitment_types=FITMENT_TYPES, labels=CONSTRUCTION_LABELS)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/pricing')
def api_pricing():
    construction = request.args.get('construction','one-piece')
    finish_tier = request.args.get('finish_tier','standard')
    db = get_db()
    rows = db.execute("SELECT size_inch, base_usd, processing_fee FROM pricing WHERE construction=? AND finish_tier=? ORDER BY size_inch",
                      (construction, finish_tier)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/wheels')
def api_wheels():
    construction = request.args.get('construction', 'all')
    db = get_db()
    if construction == 'all':
        rows = db.execute("SELECT * FROM wheels ORDER BY sort_order").fetchall()
    else:
        rows = db.execute("SELECT * FROM wheels WHERE construction=? ORDER BY sort_order", (construction,)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/quotes')
def admin_quotes():
    if request.args.get('key') != ADMIN_KEY:
        return jsonify({'error': 'unauthorized'}), 401
    db = get_db()
    rows = db.execute("SELECT * FROM quotes ORDER BY created_at DESC").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5050)

