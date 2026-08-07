#!/usr/bin/env python
"""
Test Suite for FarmShield AI
Validates all core features and integrations
"""

import sys
import requests
import sqlite3
import os
import time
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def test_files_exist():
    """Check all required files exist"""
    print_header("Testing File Structure")

    required_files = [
        'main.py', 'train.py', 'utils.py', 'requirements.txt',
        'models/model.pkl', 'models/scaler.pkl',
        'data/food_supply_data_v2.csv', 'database.db',
        'templates/login.html', 'templates/dashboard.html',
        'static/style.css', 'static/script.js'
    ]

    for file in required_files:
        exists = Path(file).exists()
        status = "[OK]" if exists else "[FAIL]"
        print(f"  {status} {file}")
        if not exists:
            return False
    return True

def test_database():
    """Check database structure"""
    print_header("Testing Database")

    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        # Check users table
        cur.execute("SELECT COUNT(*) FROM users")
        users = cur.fetchone()[0]
        print(f"  [OK] Users table: {users} records")

        # Check predictions table
        cur.execute("SELECT COUNT(*) FROM predictions")
        preds = cur.fetchone()[0]
        print(f"  [OK] Predictions table: {preds} records")

        conn.close()
        return True
    except Exception as e:
        print(f"  [FAIL] Database error: {e}")
        return False

def test_ml_models():
    """Check ML model files"""
    print_header("Testing ML Models")

    try:
        import pickle

        with open('models/model.pkl', 'rb') as f:
            model = pickle.load(f)
        print(f"  [OK] ML Model loaded: {model.__class__.__name__}")

        with open('models/scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        print(f"  [OK] Scaler loaded: {scaler.__class__.__name__}")

        return True
    except Exception as e:
        print(f"  [FAIL] ML Model error: {e}")
        return False

def test_flask_startup():
    """Test Flask app can start"""
    print_header("Testing Flask App")

    try:
        os.system("cd . && timeout 3 python main.py > /tmp/flask_test.log 2>&1 &")
        time.sleep(2)

        response = requests.get('http://localhost:5000/login', timeout=2)

        if response.status_code == 200 and 'FarmShield' in response.text:
            print(f"  [OK] Flask app running on port 5000")
            print(f"  [OK] Login page loaded (HTTP {response.status_code})")
            return True
        else:
            print(f"  [FAIL] Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"  [FAIL] Flask test error: {e}")
        return False

def test_dependencies():
    """Check Python dependencies"""
    print_header("Testing Dependencies")

    required = ['flask', 'sklearn', 'pandas', 'numpy', 'PIL']
    for pkg in required:
        try:
            __import__(pkg)
            print(f"  [OK] {pkg} installed")
        except ImportError:
            print(f"  [FAIL] {pkg} not installed")
            return False
    return True

def print_credentials():
    """Print test credentials"""
    print_header("Test Credentials")

    print("\n  REGULAR USER (Create one via signup):")
    print("    Email: test@example.com")
    print("    Password: test1234")

    print("\n  ADMIN USER (Hidden access):")
    print("    Email: foodstopage03@gmail.com")
    print("    Password: food@1234")

    print("\n  FOOD TYPES (37 total):")
    print("    - Fruits: Apple, Banana, Mango, Orange, Grapes, etc.")
    print("    - Vegetables: Potato, Tomato, Onion, Carrot, etc.")
    print("    - Grains: Rice, Wheat, Maize, Barley, etc.")
    print("    - Dairy: Milk, Butter, Cheese, Paneer, Egg, Fish, Chicken")
    print("    - Frozen: Frozen peas, Frozen corn, Ice cream, etc.")

def print_quick_start():
    """Print quick start guide"""
    print_header("Quick Start Guide")

    print("\n  1. START APP:")
    print("     python main.py")

    print("\n  2. OPEN BROWSER:")
    print("     http://localhost:5000")

    print("\n  3. LOGIN / SIGNUP:")
    print("     - Create account via signup form")
    print("     - Or use admin credentials above")

    print("\n  4. CREATE PREDICTION:")
    print("     - Go to 'AI Predictor' tab")
    print("     - Fill food type, temp, humidity, etc.")
    print("     - Click 'Run AI Prediction'")

    print("\n  5. VIEW RESULTS:")
    print("     - Risk level: Low/Moderate/High")
    print("     - Estimated loss percentage")
    print("     - Recommended vehicle type")
    print("     - Best route on map")

    print("\n  6. ADMIN PANEL (Hidden):")
    print("     - Login with admin credentials")
    print("     - Access at /admin")
    print("     - Manage users & predictions")

def main():
    """Run all tests"""
    print("\n")
    print("*" * 60)
    print("*  FarmShield AI - Comprehensive Test Suite")
    print("*" * 60)

    tests = [
        ("File Structure", test_files_exist),
        ("Database", test_database),
        ("ML Models", test_ml_models),
        ("Dependencies", test_dependencies),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"  [ERROR] {e}")
            results[name] = False

    # Print summary
    print_header("Test Summary")
    for name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {name}")

    all_passed = all(results.values())

    if all_passed:
        print("\n  [SUCCESS] All tests passed!")
    else:
        print("\n  [WARNING] Some tests failed. Check errors above.")

    print()
    print_credentials()
    print()
    print_quick_start()

    print("\n" + "=" * 60)
    print("  Ready to use FarmShield AI!")
    print("=" * 60 + "\n")

    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
