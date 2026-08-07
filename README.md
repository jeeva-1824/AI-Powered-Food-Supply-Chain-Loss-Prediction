# FarmShield AI-AI Powered Food Supply Chain Loss Prediction 

A Flask-based logistics intelligence platform for predicting food spoilage risk, optimizing transport routes, and visualizing supply chain predictions.

## Overview

FarmShield AI is an end-to-end application that combines machine learning, route visualization, weather simulation, and logistics recommendations for food supply chain transport.

Key features:
- AI-powered spoilage risk prediction
- Loss percentage and confidence estimation
- Route recommendations with Leaflet map visualization
- User signup/login and dashboard
- Admin panel for user and prediction management
- Image-based food quality analysis fallback

## Project Structure

```
AI upd/
├── .venv/                 # Python virtual environment
├── AI/                    # Main application package
│   ├── AI/
│   │   ├── main.py        # Flask application entrypoint
│   │   ├── utils.py       # ML, route, weather, and helper logic
│   │   ├── train.py       # Model training and data generation
│   │   ├── templates/     # Jinja2 views
│   │   └── static/        # CSS/JS assets
│   └── requirements.txt   # Application dependencies
├── database.db            # SQLite database (auto-created)
├── models/                # Stored model and scaler files
├── static/                # Root-level static assets
├── templates/             # Root-level templates if used by the wrapper
├── uploads/               # Uploaded images
├── main.py                # Root launcher for the AI application
└── README.md              # Project documentation
```

## Requirements

- Python 3.8+
- Windows / Linux / macOS

## 📥 Input Modes

### Mode 1: Manual Input
Enter logistics parameters:
- **Food Type** - 37+ food items pre-encoded
- **Temperature** (°C) - Current cargo temp
- **Humidity** (%) - Cargo humidity level
- **Rainfall** (mm) - Weather data
- **Transit Time** (Hours) - Estimated journey duration
- **Storage Duration** (Days) - How long product stored before transit
- **Source/Destination Coordinates** - GPS locations

### Mode 2: Image Scan
Upload photos of:
- Truck/vehicle condition
- Produce/packaging condition
- AI extracts visual features (brightness, size)
- Combines with ML prediction

### Quick Features
- **Auto Fill Sample Data** - Pre-fill realistic values
- **Use Current Location** - Auto-detect GPS coordinates

---

## 🍎 Food Type Encoding

**Fruits (9):** Apple, Banana, Mango, Orange, Grapes, Papaya, Pineapple, Guava, Watermelon

**Vegetables (9):** Potato, Tomato, Onion, Carrot, Cabbage, Cauliflower, Brinjal, Okra, Spinach

**Grains (7):** Rice, Wheat, Maize, Barley, Lentil, Chickpea, Green gram

**Dairy (7):** Milk, Butter, Cheese, Paneer, Egg, Fish, Chicken

**Frozen (5):** Frozen peas, Frozen corn, Ice cream, Ready meals, Meat products

---

## 📊 Output & Recommendations

### Risk Analysis
```
Risk Level: [Low / Moderate / High]
Loss Percentage: 0-100%
Confidence: 0-100%
```

### Route Recommendations
- **Optimal Route** (Green) - Best safety score
- **Alternate Route** (Orange) - Secondary option
- **Risky Route** (Red) - Avoid if possible

### Vehicle Suggestions
- **Refrigerated Truck** - Dairy, meat, frozen items
- **Ventilated Truck** - Fruits, leafy vegetables
- **Standard Transport** - Grains, dry goods

### Smart Advice
- Temperature warnings
- Transit timing recommendations
- Storage guidelines
- Stop location suggestions

---


## Setup and Run

1. Activate your virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

2. Run the application from the repository root:

```powershell
python main.py
```

3. Open the browser at:

```
http://localhost:5000
```

The app performs automatic setup on first run, including:
- creating `models/`, `data/`, `uploads/`, and other directories
- initializing the SQLite database
- training the machine learning model if needed

## Authentication

- Normal users can sign up and log in through the partner portal.
- A hidden admin access exists with the following credentials:
  - Email: `foodstopage03@gmail.com`
  - Password: `food@1234`

## Main App Pages

- `/login` — Login page
- `/signup` — Registration page
- `/dashboard` — User dashboard and analytics overview
- `/predict` — AI prediction form
- `/map` — Route visualization page
- `/visualization` — Prediction analytics charts
- `/about` — About page
- `/contact` — Contact/support page

## AI and Prediction Details

The prediction engine uses a trained machine learning model and helper utilities in `AI/AI/utils.py`.

Input features include:
- Temperature
- Humidity
- Rainfall
- Transit time
- Storage duration
- Food type
- Source and destination coordinates

The model outputs:
- Risk level: `Low`, `Moderate`, `High`
- Loss percentage
- Confidence score
- Suggested route and vehicle recommendation

## Notes

- The root `main.py` launcher executes the actual Flask entrypoint at `AI/AI/main.py`.
- `database.db` is generated automatically and stores users, predictions, and timestamps.
- The project uses Flask templates in `AI/AI/templates/` and static assets in `AI/AI/static/`.

## Development

- Edit application logic in `AI/AI/main.py` and `AI/AI/utils.py`.
- Templates are located in `AI/AI/templates/`.
- Use `python -m py_compile AI\AI\utils.py` to validate Python syntax.

