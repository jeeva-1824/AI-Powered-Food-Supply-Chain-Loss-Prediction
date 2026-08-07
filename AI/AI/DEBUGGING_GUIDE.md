# 🔧 FarmShield AI - Debugging & Troubleshooting Guide

Complete troubleshooting guide for common issues and solutions.

---

## ✅ Verification Checklist

Before troubleshooting, verify:

```bash
# 1. Check Python version
python --version
# Expected: Python 3.8+

# 2. Check current directory
pwd
# Expected: /path/to/Desktop/AI

# 3. List files
ls -la
# Expected: main.py, train.py, utils.py, requirements.txt, etc.

# 4. Check database
ls -la database.db
# Expected: File exists, >1MB

# 5. Check models
ls -la models/
# Expected: model.pkl (~31MB), scaler.pkl (~1KB)
```

---

## 🚨 Common Issues & Fixes

### Issue 1: "Port 5000 already in use"

**Symptom:**
```
OSError: [Errno 48] Address already in use
ERROR: Could not bind to address
```

**Solution:**

Option A - Use different port:
```bash
# Edit main.py, line ~572:
# Change: app.run(port=5000)
# To:     app.run(port=5001)
```

Option B - Kill existing process (Linux/Mac):
```bash
lsof -ti:5000 | xargs kill -9
python main.py
```

Option B - Kill existing process (Windows):
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
python main.py
```

---

### Issue 2: "ModuleNotFoundError: No module named 'flask'"

**Symptom:**
```
ModuleNotFoundError: No module named 'flask'
Traceback: import flask
```

**Solution:**

Option A - Let auto-setup install:
```bash
# Just run main.py - will auto-install
python main.py
```

Option B - Manual install:
```bash
pip install -r requirements.txt
# Or individually:
pip install Flask scikit-learn pandas numpy Pillow
```

Option C - Upgrade pip first:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### Issue 3: "FileNotFoundError: models/model.pkl"

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/model.pkl'
```

**Solution:**

Retrain model:
```bash
python train.py
```

This will:
- Generate 6000 synthetic samples
- Train RandomForest with 250 trees
- Save models/model.pkl (~31MB)
- Save models/scaler.pkl (~1KB)

Expected output:
```
[TRAIN] Generating expanded dataset...
[TRAIN] Expanded dataset saved
[TRAIN] Model Performance Accuracy: 0.8423
[TRAIN] Model saved → models/model.pkl
[TRAIN] Scaler saved → models/scaler.pkl
```

---

### Issue 4: "database.db is locked" or corrupted

**Symptom:**
```
sqlite3.OperationalError: database is locked
# OR
sqlite3.DatabaseError: file is not a database
```

**Solution:**

Option A - Delete and recreate (safe):
```bash
rm database.db
python main.py
# Database will auto-create with fresh schema
```

Option B - Check integrity:
```bash
sqlite3 database.db ".schema"
# If shows error, use Option A
```

Option C - Repair (if possible):
```bash
sqlite3 database.db "PRAGMA integrity_check;"
```

---

### Issue 5: "AttributeError: 'NoneType' object" on Login

**Symptom:**
```
AttributeError: 'NoneType' object has no attribute 'xyz'
Error at line: user = conn.execute(...).fetchone()
```

**Solution:**

Check database tables:
```bash
python << 'EOF'
import sqlite3
conn = sqlite3.connect('database.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cur.fetchall())
conn.close()
EOF
```

If tables missing:
```bash
# Delete DB and restart (auto-recreates)
rm database.db
python main.py
```

---

### Issue 6: Unicode/Emoji errors on Windows

**Symptom:**
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Solution:**

Already fixed in current version! If you still see this:

```bash
# Set environment variable
set PYTHONIOENCODING=utf-8
python main.py
```

Or edit Python start command to use UTF-8 streams.

---

### Issue 7: Geolocation not working

**Symptom:**
```
"Use Current Location" button doesn't work
GPS coordinates not auto-filled
```

**Note:** This is browser-dependent.

**Solution:**

1. Browser must grant permission
   - Look for permission popup
   - Click "Allow" when asked

2. Must be HTTPS or localhost
   - ✅ Works: http://localhost:5000
   - ✅ Works: https://yourdomain.com
   - ❌ Doesn't work: http://example.com (non-local HTTP)

3. Test browser support:
```javascript
// Open browser console (F12)
if (navigator.geolocation) {
  console.log("Geolocation supported");
  navigator.geolocation.getCurrentPosition(pos => {
    console.log("Lat:", pos.coords.latitude);
    console.log("Lon:", pos.coords.longitude);
  });
} else {
  console.log("Not supported");
}
```

---

### Issue 8: Map not loading (Leaflet error)

**Symptom:**
```
Leaflet is not defined
ReferenceError: L is undefined
Map doesn't appear
```

**Solution:**

Check internet connection (Leaflet loaded from CDN):
```bash
# Leaflet requires these CDNs:
# - https://unpkg.com/leaflet@1.9.4/dist/leaflet.css
# - https://unpkg.com/leaflet@1.9.4/dist/leaflet.js

# If offline, use local Leaflet files:
# 1. Download from leaflet.org
# 2. Save to static/
# 3. Update template CSS/JS paths
```

---

### Issue 9: Charts not displaying

**Symptom:**
```
Chart.js error
Canvas not rendering
```

**Solution:**

Check Chart.js CDN:
```bash
# Verify this CDN is accessible:
# https://cdn.jsdelivr.net/npm/chart.js@3/dist/chart.min.js

# For offline:
pip install chart.js (not available - use CDN)
# OR use local chart.js file
```

Browser console (F12):
- Check for CORS errors
- Verify canvas elements exist
- Check data format

---

### Issue 10: Image upload not working

**Symptom:**
```
Image upload fails
"File not allowed" error
Max file size exceeded
```

**Solution:**

Check file type:
- ✅ Allowed: PNG, JPG, JPEG, WEBP
- ❌ Not allowed: GIF, BMP, TIFF

Check file size:
- Maximum: 16MB (set in main.py)
- Most phones: 2-5MB is good

If still failing:
```bash
# Check uploads folder exists and is writable
mkdir -p uploads
chmod 755 uploads  # Linux/Mac
# Windows: right-click → Properties → Security
```

---

### Issue 11: Predictions not saving to database

**Symptom:**
```
Run prediction
Page refreshes
No data in history
```

**Solution:**

Check if logged in:
- Predictions save with user_id
- Must be logged in first
- Session must be active

Debug:
```bash
python << 'EOF'
import sqlite3
conn = sqlite3.connect('database.db')
cur = conn.cursor()
cur.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 1")
row = cur.fetchone()
if row:
    print("Last prediction:", row)
else:
    print("No predictions in DB")
conn.close()
EOF
```

---

### Issue 12: Admin login not working

**Symptom:**
```
Admin credentials rejected
"Invalid email or password"
```

**Solution:**

Verify exact credentials:
```
Email: foodstopage03@gmail.com  (exact)
Password: food@1234             (exact - no spaces)
```

Check in database:
```bash
python << 'EOF'
import sqlite3, hashlib
conn = sqlite3.connect('database.db')
cur = conn.cursor()
email = "foodstopage03@gmail.com"
pwd_hash = hashlib.sha256("food@1234".encode()).hexdigest()
cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, pwd_hash))
user = cur.fetchone()
print("Admin user found:", user is not None)
conn.close()
EOF
```

If not found, create admin manually:
```bash
python << 'EOF'
import sqlite3, hashlib
conn = sqlite3.connect('database.db')
cur = conn.cursor()
try:
    cur.execute(
        "INSERT INTO users(name,email,password) VALUES(?,?,?)",
        ("Admin", "foodstopage03@gmail.com",
         hashlib.sha256("food@1234".encode()).hexdigest())
    )
    conn.commit()
    print("Admin user created")
except Exception as e:
    print("Error:", e)
finally:
    conn.close()
EOF
```

---

### Issue 13: ML prediction returns incorrect results

**Symptom:**
```
Risk always "High" or always same value
Loss percentage suspicious
```

**Solution:**

Check model accuracy:
```bash
python << 'EOF'
import pickle
import numpy as np
with open('models/model.pkl', 'rb') as f:
    model = pickle.load(f)
print("Model type:", type(model))
print("Model params:", model.get_params())
EOF
```

Retrain if needed:
```bash
python train.py
```

Test prediction directly:
```bash
python << 'EOF'
import utils
result = utils.predict_risk(
    temperature=25,
    humidity=60,
    rainfall=0,
    transit_time=12,
    storage_duration=2,
    food_type_name="Rice"
)
print("Result:", result)
EOF
```

---

### Issue 14: Slow performance / Page lag

**Symptom:**
```
Predictions take >1 second
Dashboard sluggish
```

**Solution:**

Profile performance:
```bash
# Check database indexes
sqlite3 database.db ".indices"

# Add index if needed
sqlite3 database.db "CREATE INDEX IF NOT EXISTS idx_user_id ON predictions(user_id);"
```

Optimize database:
```bash
sqlite3 database.db "VACUUM;"  # Defragment
```

Check Python memory:
```bash
# Linux/Mac
ps aux | grep main.py

# If using too much memory (>200MB):
# Check for memory leaks in request handlers
```

---

### Issue 15: Browser console errors

**Symptom:**
```
F12 console shows errors
"Cannot read property X"
```

**Common Fixes:**

1. **"Undefined variable"**
   - Check HTML element IDs match JavaScript
   - Verify scripts load in correct order

2. **"CORS error"**
   - CDN resources not loading
   - Check internet connection
   - Verify CDN URLs are correct

3. **"Syntax error"**
   - Check browser supports ES6
   - Use transpiler if needed (old browser)

---

## 🧪 Testing & Validation

### Run Full Test Suite
```bash
python test.py
```

### Individual Component Tests

Test Flask app:
```bash
python << 'EOF'
from main import app
with app.test_client() as client:
    resp = client.get('/login')
    print("Login page:", resp.status_code)
EOF
```

Test database:
```bash
python << 'EOF'
import sqlite3
try:
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    print("Users:", cur.fetchone()[0])
    conn.close()
    print("Database OK")
except Exception as e:
    print("Database error:", e)
EOF
```

Test ML:
```bash
python << 'EOF'
import utils
result = utils.predict_risk(25, 60, 0, 12, 2, "Rice")
print("Prediction works:", result['risk_level'])
EOF
```

---

## 📊 Diagnostic Information

Collect this info if filing bug report:

```bash
python << 'EOF'
import sys, platform, sqlite3
import flask, sklearn, pandas, numpy, PIL, werkzeug

print("=== System Info ===")
print(f"OS: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")

print("\n=== Python Packages ===")
print(f"Flask: {flask.__version__}")
print(f"scikit-learn: {sklearn.__version__}")
print(f"pandas: {pandas.__version__}")
print(f"numpy: {numpy.__version__}")
print(f"Pillow: {PIL.__version__}")
print(f"Werkzeug: {werkzeug.__version__}")

print("\n=== Database ===")
conn = sqlite3.connect('database.db')
print(f"SQLite: {sqlite3.version}")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM users")
print(f"Users: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM predictions")
print(f"Predictions: {cur.fetchone()[0]}")
conn.close()

print("\n=== Models ===")
import os
print(f"model.pkl exists: {os.path.exists('models/model.pkl')}")
print(f"scaler.pkl exists: {os.path.exists('models/scaler.pkl')}")

print("\n=== Dataset ===")
print(f"food_supply_data_v2.csv exists: {os.path.exists('data/food_supply_data_v2.csv')}")
EOF
```

---

## 📞 Getting Help

If stuck:

1. **Check test.py output**
   ```bash
   python test.py
   ```

2. **Read error message carefully**
   - Note exact error text
   - Check line number

3. **Check browser console** (F12)
   - JavaScript errors?
   - Network errors?

4. **Check Flask terminal output**
   - Does Flask show request?
   - Any Python errors?

5. **Restart everything**
   ```bash
   # Kill Flask (Ctrl+C)
   # Delete database.db if corrupted
   rm database.db
   # Start fresh
   python main.py
   ```

---

## ✅ Confirmation Checklist

After fixing any issue, verify:

- [ ] App starts without errors
- [ ] Can access login page
- [ ] Can create user account
- [ ] Can login with new user
- [ ] Can make a prediction
- [ ] Results display correctly
- [ ] Can access dashboard
- [ ] Charts render
- [ ] Map loads
- [ ] Can logout
- [ ] Admin can login (if applicable)
- [ ] Admin can manage users
- [ ] Database exports successfully

---

**Still stuck? Try this nuclear option:**

```bash
# Fresh start (WARNING: deletes data!)
rm database.db
python train.py
python main.py
```

---

**FarmShield AI Support © 2024**
