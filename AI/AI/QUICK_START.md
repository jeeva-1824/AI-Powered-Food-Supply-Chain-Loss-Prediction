# 🚀 FarmShield AI - Quick Start Guide

Get the AI Food Supply Chain Loss Predictor running in **30 seconds!**

---

## ⚡ Ultra-Quick Start

### Step 1: Run the App
```bash
python main.py
```

**That's it!** The app will:
- ✅ Auto-install dependencies
- ✅ Create database
- ✅ Train ML model (first run only)
- ✅ Open browser automatically
- ✅ Run on http://localhost:5000

---

## 📋 What You Get

After starting, you'll have:

```
✓ Full-stack web app with authentication
✓ AI-powered spoilage prediction system
✓ Interactive route mapping
✓ Real-time logistics intelligence
✓ Admin panel (hidden access)
✓ Multi-user support
✓ Production-grade security
```

---

## 👤 Test Accounts

### Admin Access (Hidden)
```
URL: http://localhost:5000/admin
Email: foodstopage03@gmail.com
Password: food@1234
```

### Create Your Own User
1. Go to "Sign Up" on login page
2. Enter Name, Email, Password
3. Click "Create partner account"
4. Login with your credentials

---

## 🎯 Try a Prediction

1. **Login** (create account or use admin)
2. **Go to "AI Predictor"**
3. **Fill in logistics data:**
   - Food type: Select from dropdown (37 options)
   - Temperature: 25°C (enter your value)
   - Humidity: 60% (enter your value)
   - Transit time: 12 hours
   - Rainfall: 0 mm
   - Storage duration: 2 days

4. **Click "Auto Fill Sample Data"** for realistic values

5. **Click "Run AI Prediction"**

6. **See results:**
   - Risk Level (Low/Moderate/High)
   - Estimated Loss %
   - Recommended vehicle
   - Best route options

---

## 🗺️ Interactive Map Features

On the prediction result page:
- **Click map** to set source/destination
- **View 3 routes:** Optimal (green), Alternate (orange), Risky (red)
- **See distance** in km and estimated time
- **View safe stop** location

---

## 📊 Dashboard Features

After making predictions, view:
- **Total Predictions** counter
- **Risk Distribution** pie chart
- **Loss Trends** line chart
- **Recent Activity** table
- **System Stats** (accuracy, status)

---

## 👨‍💼 Admin Panel (Hidden Access)

Login as admin to access:

### User Management
```
/admin/users
- View all registered users
- Search by name/email
- Edit user details
- Delete user accounts
```

### Prediction Audit
```
/admin/predictions
- View all predictions ever made
- Filter by user
- Delete prediction records
```

### Database Backup
```
/admin/database
- Download complete database.db file
- Export all data
- Backup for analysis
```

---

## 🎨 UI Features

### Responsive Design
- **Desktop:** Full sidebar + content
- **Tablet:** Collapsible sidebar
- **Mobile:** Hamburger menu

### Visual Effects
- ✨ Truck animation on page transitions
- 📍 Loading spinners
- 📱 Toast notifications
- 🎨 Smooth gradients

### Dark Admin Panel
- Separate UI for admins
- Dark theme
- System monitoring stats

---

## 🍎 Available Food Types (37)

### Fruits (9)
Apple • Banana • Mango • Orange • Grapes • Papaya • Pineapple • Guava • Watermelon

### Vegetables (9)
Potato • Tomato • Onion • Carrot • Cabbage • Cauliflower • Brinjal • Okra • Spinach

### Grains (7)
Rice • Wheat • Maize • Barley • Lentil • Chickpea • Green gram

### Dairy (7)
Milk • Butter • Cheese • Paneer • Egg • Fish • Chicken

### Frozen (5)
Frozen peas • Frozen corn • Ice cream • Ready meals • Meat products

---

## 🤖 How the AI Works

**Model:** RandomForest with 250 trees

**Analyzes:**
- Temperature & humidity
- Rainfall & weather
- Transit time
- Storage duration
- Food perishability

**Outputs:**
- Risk Level: Low / Moderate / High
- Loss Percentage: 0-100%
- Confidence: 0-100%

**Accuracy:** 84% on test data

---

## 🔒 Security

- ✅ SHA-256 password hashing
- ✅ Server-side sessions
- ✅ CSRF protection
- ✅ Email validation
- ✅ Admin access control
- ✅ Duplicate email prevention

---

## 🛠️ Project Structure

```
/Desktop/AI/
├── main.py              ← Run this!
├── train.py             ← ML model training
├── utils.py             ← Helper functions
├── test.py              ← Test suite
├── requirements.txt     ← Dependencies
├── README.md            ← Full documentation
│
├── models/
│   ├── model.pkl       (AI model)
│   └── scaler.pkl      (data normalizer)
│
├── data/
│   └── food_supply_data_v2.csv  (6000 training samples)
│
├── templates/           (HTML pages)
├── static/              (CSS, JS, images)
├── uploads/             (user image uploads)
└── database.db          (SQLite database)
```

---

## 📱 API Endpoints (For Developers)

```
POST /api/predict
  Parameters: temperature, humidity, rainfall, transit_time,
              storage_duration, food_type
  Returns: {risk_level, loss_percentage, confidence, probabilities}

GET /api/weather?lat=X&lon=Y
  Returns: {temperature, humidity, condition}
```

---

## ❌ Troubleshooting

### "Port 5000 already in use"
```bash
# Use different port (edit main.py line 572):
app.run(debug=False, host='0.0.0.0', port=5001)
```

### "ModuleNotFoundError"
```bash
# Reinstall dependencies:
pip install -r requirements.txt
```

### "Model files not found"
```bash
# Retrain model:
python train.py
```

### "Database error"
```bash
# Reset database:
rm database.db
python main.py  # Auto-creates fresh DB
```

---

## 📊 Test the System

Run the test suite:
```bash
python test.py
```

Verifies:
- ✓ All files exist
- ✓ Database is healthy
- ✓ ML models loaded
- ✓ Dependencies installed
- ✓ Flask app starts

---

## 🚀 Deployment

### Local (Development)
```bash
python main.py
```

### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn main:app --bind 0.0.0.0:5000
```

### Replit
1. Fork repo to Replit
2. Click "Run"
3. Share link with button "Open in new tab"

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

---

## 💡 Pro Tips

1. **Use "Auto Fill"** to populate sample realistic data
2. **Use "Current Location"** to auto-detect your GPS
3. **Click the map** to adjust source/destination coordinates
4. **Try different food types** to see how risk changes
5. **Check admin panel** for system statistics

---

## 📞 Support

- **Issues?** Check the full README.md
- **API docs?** See main.py route definitions
- **ML details?** See train.py and utils.py

---

## 🎯 Next Steps

1. ✅ Start app: `python main.py`
2. ✅ Try a prediction
3. ✅ Explore the map
4. ✅ Login as admin
5. ✅ Download database backup
6. ✅ Invite other users!

---

**FarmShield AI © 2024**

*Predict spoilage. Optimize logistics. Reduce waste. 🌾*
