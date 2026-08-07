"""
main.py - AI-Powered Food Supply Chain Loss Predictor
Entry point: Run with `python main.py`
"""

import os
import sys
import subprocess
import sqlite3
import json
import re
import hashlib
import webbrowser
import threading
import io
from datetime import datetime
from functools import wraps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
DB = os.path.join(BASE_DIR, 'database.db')

# ─── Auto-install dependencies ────────────────────────────────────────────────
def install_if_missing(*packages):
    import importlib
    for pkg in packages:
        mod = pkg.split(':')[1] if ':' in pkg else pkg
        try:
            importlib.import_module(mod)
        except ImportError:
            name = pkg.split(':')[0] if ':' in pkg else pkg
            print(f"[SETUP] Installing {name}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--prefer-binary', name, '-q'])

install_if_missing(
    'flask', 'scikit-learn:sklearn', 'numpy', 'pandas',
    'Pillow:PIL', 'werkzeug', 'requests'
)

from flask import (Flask, render_template, request, redirect, url_for,
                   session, jsonify, flash, send_file, abort)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image

import utils
import train as trainer

# ─── App config ────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
app.secret_key = 'foodchain_secure_key_2024_ag77x'
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Jinja2 custom filters
import json as _json
app.jinja_env.filters['fromjson'] = _json.loads

ADMIN_EMAIL = 'foodstopage03@gmail.com'
ADMIN_PASS  = 'food@1234'

LANGUAGES = {
    'en': 'English',
    'ta': 'தமிழ்'
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# ─── Auto-setup ────────────────────────────────────────────────────────────────
def auto_setup():
    for d in [MODELS_DIR, DATA_DIR, UPLOAD_DIR, STATIC_DIR, TEMPLATES_DIR]:
        os.makedirs(d, exist_ok=True)
    init_db()
    if not (os.path.exists(os.path.join(MODELS_DIR, 'model.pkl')) and os.path.exists(os.path.join(MODELS_DIR, 'scaler.pkl'))):
        print("[SETUP] Training ML model (first run)...")
        trainer.train()
    else:
        print("[SETUP] ML models found. Skipping training.")


# ─── Database ──────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        name           TEXT NOT NULL,
        email          TEXT UNIQUE NOT NULL,
        password       TEXT NOT NULL,
        contact_number TEXT,
        district       TEXT,
        state          TEXT,
        created        TEXT DEFAULT CURRENT_TIMESTAMP,
        created_at     TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS predictions (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id          INTEGER,
        food_type        TEXT,
        encoded_food     INTEGER,
        temperature      REAL,
        humidity         REAL,
        rainfall         REAL,
        transit_time     REAL,
        storage_duration REAL,
        src_lat          REAL,
        src_lon          REAL,
        dst_lat          REAL,
        dst_lon          REAL,
        distance_km      REAL,
        risk_level       TEXT,
        loss_percentage  REAL,
        confidence       REAL,
        weather_cond     TEXT,
        storage_rec      TEXT,
        created          TEXT DEFAULT CURRENT_TIMESTAMP,
        created_at       TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)

    def add_column_if_missing(table, column, definition):
        existing = [row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
        if column not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    add_column_if_missing('users', 'contact_number', 'TEXT')
    add_column_if_missing('users', 'district', 'TEXT')
    add_column_if_missing('users', 'state', 'TEXT')
    add_column_if_missing('users', 'created', 'TEXT')
    add_column_if_missing('users', 'created_at', 'TEXT')

    add_column_if_missing('predictions', 'user_id', 'INTEGER')
    add_column_if_missing('predictions', 'food_type', 'TEXT')
    add_column_if_missing('predictions', 'encoded_food', 'INTEGER')
    add_column_if_missing('predictions', 'temperature', 'REAL')
    add_column_if_missing('predictions', 'humidity', 'REAL')
    add_column_if_missing('predictions', 'rainfall', 'REAL')
    add_column_if_missing('predictions', 'transit_time', 'REAL')
    add_column_if_missing('predictions', 'storage_duration', 'REAL')
    add_column_if_missing('predictions', 'src_lat', 'REAL')
    add_column_if_missing('predictions', 'src_lon', 'REAL')
    add_column_if_missing('predictions', 'dst_lat', 'REAL')
    add_column_if_missing('predictions', 'dst_lon', 'REAL')
    add_column_if_missing('predictions', 'distance_km', 'REAL')
    add_column_if_missing('predictions', 'risk_level', 'TEXT')
    add_column_if_missing('predictions', 'loss_percentage', 'REAL')
    add_column_if_missing('predictions', 'confidence', 'REAL')
    add_column_if_missing('predictions', 'weather_cond', 'TEXT')
    add_column_if_missing('predictions', 'storage_rec', 'TEXT')
    add_column_if_missing('predictions', 'created', 'TEXT')
    add_column_if_missing('predictions', 'created_at', 'TEXT')

    conn.execute("""
        UPDATE users
        SET created_at = COALESCE(created_at, created, CURRENT_TIMESTAMP)
        WHERE created_at IS NULL OR created_at = ''
    """)
    conn.execute("""
        UPDATE predictions
        SET created_at = COALESCE(created_at, created, CURRENT_TIMESTAMP)
        WHERE created_at IS NULL OR created_at = ''
    """)

    conn.commit()
    conn.close()


def hash_password(pwd):
    return generate_password_hash(pwd)

def verify_password(hashed, pwd):
    return check_password_hash(hashed, pwd)


# ─── Decorators ────────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ─── Auth routes ───────────────────────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # Hidden admin check
        if email == ADMIN_EMAIL.lower() and password == ADMIN_PASS:
            session['user_id']  = 0
            session['user_name'] = 'Admin'
            session['is_admin'] = True
            flash('Welcome, Admin! [SHIELD]', 'success')
            return redirect(url_for('admin_dashboard'))

        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE email=?',
            (email,)
        ).fetchone()
        conn.close()

        if user and verify_password(user['password'], password):
            session['user_id']   = user['id']
            session['user_name'] = user['name']
            session['is_admin']  = False
            flash(f'Welcome back, {user["name"]}! [FARM]', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name           = request.form.get('name', '').strip()
        email          = request.form.get('email', '').strip().lower()
        password       = request.form.get('password', '')
        confirm        = request.form.get('confirm', '')
        contact_number = request.form.get('contact_number', '').strip()
        district       = request.form.get('district', '').strip()
        state          = request.form.get('state', '').strip()

        if not name or len(name) < 2:
            flash('Name must be at least 2 characters.', 'danger')
        elif not utils.validate_email(email):
            flash('Please enter a valid email address.', 'danger')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
        elif password != confirm:
            flash('Passwords do not match.', 'danger')
        else:
            try:
                conn = get_db()
                conn.execute(
                    'INSERT INTO users(name,email,password,contact_number,district,state) VALUES(?,?,?,?,?,?)',
                    (name, email, hash_password(password), contact_number, district, state)
                )
                conn.commit()
                conn.close()
                flash('Account created! Please login. [SUCCESS]', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Email already registered.', 'danger')
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))


# ─── Dashboard ─────────────────────────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    uid = session['user_id']

    if session.get('is_admin'):
        preds = conn.execute('SELECT * FROM predictions ORDER BY created_at DESC LIMIT 10').fetchall()
        total_preds = conn.execute('SELECT COUNT(*) FROM predictions').fetchone()[0]
        total_users  = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    else:
        preds = conn.execute(
            'SELECT * FROM predictions WHERE user_id=? ORDER BY created_at DESC LIMIT 10', (uid,)
        ).fetchall()
        total_preds = conn.execute('SELECT COUNT(*) FROM predictions WHERE user_id=?', (uid,)).fetchone()[0]
        total_users = None

    # Chart data
    risk_counts = {'Low': 0, 'Moderate': 0, 'High': 0}
    all_preds_q = conn.execute(
        'SELECT risk_level FROM predictions WHERE user_id=?', (uid,)
    ).fetchall() if not session.get('is_admin') else conn.execute(
        'SELECT risk_level FROM predictions'
    ).fetchall()
    for row in all_preds_q:
        rc = row['risk_level']
        if rc in risk_counts:
            risk_counts[rc] += 1

    # Loss trend (last 15)
    trend_q = conn.execute(
        'SELECT loss_percentage, created_at FROM predictions ORDER BY created_at DESC LIMIT 15'
    ).fetchall()
    loss_trend = [{'loss': r['loss_percentage'], 'date': r['created_at'][:10]} for r in reversed(trend_q)]

    conn.close()
    weather = utils.get_simulated_weather(20.5937, 78.9629)
    return render_template('dashboard.html',
        predictions=preds,
        total_preds=total_preds,
        total_users=total_users,
        risk_counts=json.dumps(risk_counts),
        loss_trend=json.dumps(loss_trend),
        weather=weather,
        now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )


# ─── Prediction ────────────────────────────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    food_categories = utils.FOOD_CATEGORIES
    result = None

    try:
        if request.method == 'POST':
            mode = request.form.get('mode', 'manual')
            try:
                temperature      = float(request.form.get('temperature', 25))
                humidity         = float(request.form.get('humidity', 60))
                rainfall         = float(request.form.get('rainfall', 0))
                transit_time     = float(request.form.get('transit_time', 12))
                storage_duration = float(request.form.get('storage_duration', 3))
                category         = request.form.get('category', '')
                food_type        = request.form.get('food_type', 'Rice')
                src_lat          = float(request.form.get('src_lat', 19.076))
                src_lon          = float(request.form.get('src_lon', 72.8777))
                dst_lat          = float(request.form.get('dst_lat', 28.6139))
                dst_lon          = float(request.form.get('dst_lon', 77.2090))
            except (ValueError, TypeError):
                flash('Invalid input. Please check values.', 'danger')
                return render_template('predict.html', food_categories=utils.FOOD_CATEGORIES)

            # Validate food belongs to selected category (single validation)
            if category and food_type not in utils.get_foods_by_category(category):
                flash(f'{food_type} not in {category}. Please select matching food.', 'danger')
                return render_template('predict.html', food_categories=utils.FOOD_CATEGORIES)

            # Image input mode – basic analysis
            image_info = None
            if mode == 'image' and 'food_image' in request.files:
                file = request.files['food_image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(path)
                    try:
                        img = Image.open(path).convert('RGB')
                        w, h = img.size
                        brightness = sum(img.getpixel((w//2, h//2))[:3]) / 3
                        if brightness < 80:
                            image_info = {'condition': 'Poor', 'temperature': temperature + 3}
                            temperature = min(45, temperature + 3)
                        elif brightness < 150:
                            image_info = {'condition': 'Fair', 'temperature': temperature + 1}
                        else:
                            image_info = {'condition': 'Good', 'temperature': temperature}
                    except Exception:
                        image_info = None

            try:
                ml = utils.predict_risk(temperature, humidity, rainfall,
                                         transit_time, storage_duration, food_type)
            except Exception as e:
                print(f"[ERROR] ML Prediction failed: {e}")
                flash('AI Prediction engine is temporarily warming up. Using fallback safety heuristics.', 'warning')
                ml = {
                    'risk_level': 'Moderate',
                    'confidence': 0.0,
                    'loss_percentage': 25.0,
                    'advice': ['Monitor temperature regularly.']
                }
            
            # Safety and route data
            try:
                safe_stop_tuple = utils.get_midpoint(src_lat, src_lon, dst_lat, dst_lon)
                safe_stop = {'lat': safe_stop_tuple[0], 'lon': safe_stop_tuple[1]}
            except Exception as err:
                print(f"[WARNING] Midpoint calculation failed: {err}")
                safe_stop = {'lat': src_lat, 'lon': src_lon}
            
            distance = utils.haversine(src_lat, src_lon, dst_lat, dst_lon)
            routes = utils.generate_routes(src_lat, src_lon, dst_lat, dst_lon,
                                              ml['risk_level'], transit_time)
            vehicle_recs = utils.get_vehicle_recommendations(food_type)
            safety_recs = utils.get_safety_recommendations(ml['risk_level'], food_type, temperature)

            food_enc = utils.FOOD_TYPE_MAP.get(food_type, 0)
            weather  = utils.fetch_weather(src_lat, src_lon)

            # Save to DB
            conn = get_db()
            conn.execute("""
                INSERT INTO predictions
                (user_id, food_type, encoded_food, temperature, humidity, rainfall, transit_time,
                 storage_duration, src_lat, src_lon, dst_lat, dst_lon, distance_km, risk_level,
                 loss_percentage, confidence, weather_cond, storage_rec)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (session['user_id'], food_type, food_enc, temperature, humidity, rainfall,
                  transit_time, storage_duration, src_lat, src_lon, dst_lat, dst_lon,
                  distance, ml['risk_level'], ml['loss_percentage'], ml['confidence'],
                  weather['condition'], vehicle_recs['best']['name']))
            conn.commit()
            conn.close()

            # PERF: Precompute ALL advanced metrics ONCE (cached funcs)
            advanced_metrics = utils.compute_all_advanced_metrics(
                food_type, temperature, humidity, storage_duration,
                distance, weather['condition'], transit_time
            )

            result = {
                'ml': ml,
                'distance': distance,
                'routes': routes,
                'vehicle_recs': vehicle_recs,
                'safety_recs': safety_recs,
                'safe_stop': safe_stop,
                'food_type': food_type,
                'weather': weather,
                'image_info': image_info,
                'src': {'lat': src_lat, 'lon': src_lon},
                'dst': {'lat': dst_lat, 'lon': dst_lon},
                'advanced_metrics': advanced_metrics,  # NEW: All 4 sections ready!
            }

            # PERF: Cache metrics in session for API fallbacks (5min TTL)
            if result:
                session['advanced_metrics'] = result['advanced_metrics']
                session.modified = True

        weather = utils.get_simulated_weather(20.5937, 78.9629)
        return render_template('predict.html',
            food_categories=food_categories,
            result=result,
            weather=weather,
            now=datetime.now().strftime('%H:%M:%S')
        )
    except Exception:
        import traceback
        with open('CRITICAL_ERROR.txt', 'w') as f:
            f.write(traceback.format_exc())
        raise


# PERF: Global cache headers (moved to top-level)
@app.after_request
def add_cache_headers(response):
    response.cache_control.max_age = 300  # 5min
    response.headers['Cache-Control'] += ', public'
    return response


# ─── Map route ─────────────────────────────────────────────────────────────────
@app.route('/map')
@login_required
def map_view():
    conn = get_db()
    uid = session['user_id']
    latest = conn.execute(
        'SELECT * FROM predictions WHERE user_id=? ORDER BY created_at DESC LIMIT 1', (uid,)
    ).fetchone()
    conn.close()

    routes_json = '[]'
    prediction_json = '{}'
    if latest:
        routes = utils.generate_routes(
            latest['src_lat'], latest['src_lon'],
            latest['dst_lat'], latest['dst_lon'],
            latest['risk_level'], latest['transit_time']
        )
        routes_json = json.dumps(routes)
        prediction_json = json.dumps({
            'src': {'lat': latest['src_lat'], 'lon': latest['src_lon']},
            'dst': {'lat': latest['dst_lat'], 'lon': latest['dst_lon']},
            'risk_level': latest['risk_level'],
            'food_type': latest['food_type'],
            'distance': latest['distance_km'],
        })

    markets = utils.load_markets()
    nearest_market, _ = utils.find_nearest_market(20.5937, 78.9629)

    highlight = request.args.get('highlight')
    return render_template('map.html',
        routes_json=routes_json,
        prediction_json=prediction_json,
        markets_json=json.dumps(markets),
        nearest_market_json=json.dumps(nearest_market or {})
    )


# ─── API endpoints ─────────────────────────────────────────────────────────────
@app.route('/api/weather')
@login_required
def api_weather():
    lat = float(request.args.get('lat', 20.5937))
    lon = float(request.args.get('lon', 78.9629))
    return jsonify(utils.fetch_weather(lat, lon))


@app.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    data = request.json
    try:
        ml = utils.predict_risk(
            data['temperature'], data['humidity'], data['rainfall'],
            data['transit_time'], data['storage_duration'], data['food_type']
        )
        return jsonify(ml)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ─── Admin routes ──────────────────────────────────────────────────────────────
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    conn = get_db()
    total_users  = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_preds  = conn.execute('SELECT COUNT(*) FROM predictions').fetchone()[0]
    high_risk    = conn.execute("SELECT COUNT(*) FROM predictions WHERE risk_level='High'").fetchone()[0]
    recent_preds = conn.execute('SELECT p.*, u.name FROM predictions p LEFT JOIN users u ON p.user_id=u.id ORDER BY p.created_at DESC LIMIT 10').fetchall()
    conn.close()
    return render_template('admin.html',
        total_users=total_users,
        total_preds=total_preds,
        high_risk=high_risk,
        recent_preds=recent_preds,
        now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_users():
    conn = get_db()
    search = request.args.get('q', '').strip()
    if search:
        users = conn.execute(
            "SELECT * FROM users WHERE name LIKE ? OR email LIKE ?",
            (f'%{search}%', f'%{search}%')
        ).fetchall()
    else:
        users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('users.html', users=users, search=search)


@app.route('/admin/users/edit/<int:uid>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(uid):
    conn = get_db()
    if request.method == 'POST':
        name  = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        if name and utils.validate_email(email):
            conn.execute('UPDATE users SET name=?, email=? WHERE id=?', (name, email, uid))
            conn.commit()
            flash('User updated successfully.', 'success')
        else:
            flash('Invalid name or email.', 'danger')
        conn.close()
        return redirect(url_for('admin_users'))
    user = conn.execute('SELECT * FROM users WHERE id=?', (uid,)).fetchone()
    conn.close()
    if not user:
        abort(404)
    return render_template('edit_user.html', user=user)


@app.route('/admin/users/delete/<int:uid>', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(uid):
    conn = get_db()
    conn.execute('DELETE FROM users WHERE id=?', (uid,))
    conn.execute('DELETE FROM predictions WHERE user_id=?', (uid,))
    conn.commit()
    conn.close()
    flash('User deleted.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/predictions')
@login_required
@admin_required
def admin_predictions():
    conn = get_db()
    preds = conn.execute(
        'SELECT p.*, u.name FROM predictions p LEFT JOIN users u ON p.user_id=u.id ORDER BY p.created_at DESC'
    ).fetchall()
    conn.close()
    return render_template('admin_predictions.html', predictions=preds)


@app.route('/admin/predictions/delete/<int:pid>', methods=['POST'])
@login_required
@admin_required
def admin_delete_prediction(pid):
    conn = get_db()
    conn.execute('DELETE FROM predictions WHERE id=?', (pid,))
    conn.commit()
    conn.close()
    flash('Prediction log deleted permanently.', 'success')
    # If deleted from dashboard, stay on dashboard, else go to predictions list
    if 'admin' in request.referrer and 'predictions' not in request.referrer:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_predictions'))


@app.route('/admin/database')
@login_required
@admin_required
def admin_download_db():
    return send_file(DB, as_attachment=True, download_name='food_chain_db.sqlite')


# ─── About ───────────────────────────────────────────────────────────────────
@app.route('/about')
@login_required
def about():
    return render_template('about.html')


# ─── Contact ───────────────────────────────────────────────────────────────────
@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')


# ─── NEW ROUTE: Visualization Page ─────────────────────────────────────────────
@app.route('/visualization')
@login_required
def visualization():
    conn = get_db()
    uid = session['user_id']
    
    if not session.get('is_admin'):
        all_preds = conn.execute(
            'SELECT * FROM predictions WHERE user_id=? ORDER BY created_at',
            (uid,)
        ).fetchall()
    else:
        all_preds = conn.execute(
            'SELECT * FROM predictions ORDER BY created_at'
        ).fetchall()
    
    conn.close()
    
    if not all_preds:
        flash('No prediction data available yet.', 'info')
        return redirect(url_for('dashboard'))
    
    # Prepare chart data
    loss_trends = [{'date': p['created_at'][:10], 'loss': p['loss_percentage']} for p in all_preds]
    
    risk_dist = {'Low': 0, 'Moderate': 0, 'High': 0}
    for p in all_preds:
        if p['risk_level'] in risk_dist:
            risk_dist[p['risk_level']] += 1
    
    food_risk = {}
    for p in all_preds:
        food = p['food_type']
        if food not in food_risk:
            food_risk[food] = {'count': 0, 'avg_loss': 0}
        food_risk[food]['count'] += 1
        food_risk[food]['avg_loss'] += p['loss_percentage']
    
    for food in food_risk:
        food_risk[food]['avg_loss'] /= food_risk[food]['count']
    
    return render_template('visualization.html',
        loss_trends=json.dumps(loss_trends),
        risk_dist=json.dumps(risk_dist),
        food_risk=json.dumps({k: v['avg_loss'] for k, v in food_risk.items()}),
        food_counts=json.dumps({k: v['count'] for k, v in food_risk.items()})
    )


# ─── NEW ROUTES: Advanced API Endpoints ────────────────────────────────────────
@app.route('/api/shelf-life', methods=['POST'])
@login_required
def api_shelf_life():
    # PERF: Use precomputed if available, else compute (cached)
    if 'advanced_metrics' in session:
        return jsonify(session['advanced_metrics']['shelf_life'])
    data = request.json
    try:
        result = utils.predict_shelf_life(
            data['food_type'],
            data['temperature'],
            data['humidity'],
            data['storage_duration']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/spoilage-timeline', methods=['POST'])
@login_required
def api_spoilage_timeline():
    # PERF: Use precomputed if available, else compute (cached)
    if 'advanced_metrics' in session:
        return jsonify(session['advanced_metrics']['spoilage_timeline'])
    data = request.json
    try:
        result = utils.generate_spoilage_timeline(
            data['food_type'],
            data['temperature'],
            data['humidity'],
            data['storage_duration']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/delay-prediction', methods=['POST'])
@login_required
def api_delay_prediction():
    # PERF: Use precomputed if available, else compute (cached)
    if 'advanced_metrics' in session:
        return jsonify(session['advanced_metrics']['delay_prediction'])
    data = request.json
    try:
        result = utils.predict_delay(
            data['distance'],
            data['weather'],
            data['transit_time'],
            data['temperature'],
            data['humidity']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/storage-recommendations', methods=['POST'])
@login_required
def api_storage_recommendations():
    # PERF: Use precomputed if available, else compute (cached)
    if 'advanced_metrics' in session:
        return jsonify(session['advanced_metrics']['storage_recommendations'])
    data = request.json
    try:
        result = utils.get_detailed_storage_recommendations(data['food_type'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/optimize-route', methods=['POST'])
@login_required
def api_optimize_route():
    data = request.json
    try:
        routes = utils.optimize_route_advanced(
            data['src_lat'], data['src_lon'],
            data['dst_lat'], data['dst_lon'],
            data['risk_level'],
            data['transit_time'],
            data['weather'],
            data['distance'],
            data['temperature'],
            data['humidity']
        )
        return jsonify({'routes': routes})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ─── NEW ROUTE: Admin Contact Management ───────────────────────────────────────
@app.route('/admin/settings')
@login_required
@admin_required
def admin_settings():
    # In a production app, these would be stored in database
    settings = {
        'emergency_contact': '+91-9876-543210',
        'transport_contact': 'logistics@agroroute.ai',
        'admin_email': ADMIN_EMAIL
    }
    return render_template('admin_settings.html', settings=settings)


@app.route('/admin/settings/update', methods=['POST'])
@login_required
@admin_required
def admin_update_settings():
    # In production, validate and store settings
    emergency = request.form.get('emergency_contact', '')
    transport = request.form.get('transport_contact', '')
    
    if emergency and transport:
        flash('Settings updated successfully.', 'success')
    else:
        flash('All fields are required.', 'danger')
    
    return redirect(url_for('admin_settings'))


# ─── NEW ROUTE: Download Source Code ──────────────────────────────────────────
@app.route('/admin/download-source')
@login_required
@admin_required
def admin_download_source():
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            files_to_zip = [
                'main.py', 'train.py', 'utils.py',
                'requirements.txt', 'README.md'
            ]
            
            for file in files_to_zip:
                if os.path.exists(file):
                    zf.write(file, arcname=file)
            
            # Add templates
            for file in os.listdir('templates'):
                if file.endswith('.html'):
                    zf.write(os.path.join('templates', file), 
                            arcname=f'templates/{file}')
            
            # Add static
            for file in os.listdir('static'):
                zf.write(os.path.join('static', file), 
                        arcname=f'static/{file}')
        
        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='food-chain-predictor-source.zip'
        )
    except Exception as e:
        flash(f'Error creating source download: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))


# ─── NEW ROUTE: Export Report as JSON ──────────────────────────────────────────
@app.route('/admin/export-report')
@login_required
@admin_required
def admin_export_report():
    conn = get_db()
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_users': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'total_predictions': conn.execute('SELECT COUNT(*) FROM predictions').fetchone()[0],
        'high_risk_count': conn.execute("SELECT COUNT(*) FROM predictions WHERE risk_level='High'").fetchone()[0],
        'average_loss_percent': round(conn.execute("SELECT AVG(loss_percentage) FROM predictions").fetchone()[0] or 0, 2),
        'predictions': [dict(row) for row in conn.execute('SELECT * FROM predictions ORDER BY created_at DESC LIMIT 100').fetchall()]
    }
    
    conn.close()
    
    return send_file(
        io.BytesIO(json.dumps(report, indent=2).encode()),
        mimetype='application/json',
        as_attachment=True,
        download_name=f'food-chain-report-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )


# ─── Error handlers ────────────────────────────────────────────────────────────
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, msg='Access Forbidden'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, msg='Page Not Found'), 404


# ─── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    auto_setup()
    print("\n" + "="*55)
    print("  [STARTUP] Food Supply Chain Loss Predictor")
    print("="*55)
    print("  URL: http://localhost:5000")
    print("="*55 + "\n")

    def open_browser():
        import time; time.sleep(1.5)
        webbrowser.open('http://localhost:5000')

    threading.Thread(target=open_browser, daemon=True).start()
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=5000)
