"""
train.py - ML Training Script for Food Supply Chain Loss Predictor
Trains a RandomForestClassifier with MinMaxScaler
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
import warnings
warnings.filterwarnings('ignore')

from utils import FOOD_TYPE_MAP, RISK_LABELS


def generate_synthetic_dataset(n_samples=6000):
    """Generate a realistic synthetic food supply chain dataset."""
    np.random.seed(42)
    food_types = list(FOOD_TYPE_MAP.keys())
    data = []
    for _ in range(n_samples):
        food = np.random.choice(food_types)
        food_enc = FOOD_TYPE_MAP[food]
        temperature = np.random.uniform(2, 45)
        humidity = np.random.uniform(20, 95)
        rainfall = np.random.uniform(0, 200)
        transit_time = np.random.uniform(0.5, 72)
        storage_duration = np.random.uniform(0, 30)

        risk_score = 0
        if temperature > 35:
            risk_score += 2.5
        elif temperature > 28:
            risk_score += 1.2
        if humidity > 80:
            risk_score += 1.8
        elif humidity > 65:
            risk_score += 0.6
        if transit_time > 40:
            risk_score += 2.2
        elif transit_time > 20:
            risk_score += 1.1
        if storage_duration > 12:
            risk_score += 1.6
        elif storage_duration > 6:
            risk_score += 0.7

        if food_enc in [25, 28, 29, 30, 31, 17, 16, 34]:
            risk_score += 2.0
        elif food_enc in [1, 2, 5, 10, 13, 14, 15, 8]:
            risk_score += 0.9
        if rainfall > 120:
            risk_score += 0.7
        risk_score += np.random.uniform(-0.8, 1.2)

        if risk_score < 3.0:
            label = 0
            loss_pct = np.random.uniform(1, 10)
        elif risk_score < 5.2:
            label = 1
            loss_pct = np.random.uniform(10, 30)
        else:
            label = 2
            loss_pct = np.random.uniform(30, 75)

        data.append([
            temperature, humidity, rainfall, transit_time,
            storage_duration, food_enc, label, round(loss_pct, 2)
        ])

    df = pd.DataFrame(data, columns=[
        'temperature', 'humidity', 'rainfall', 'transit_time',
        'storage_duration', 'food_type_encoded', 'risk_label', 'loss_percentage'
    ])
    return df


def load_dataset():
    """Load real dataset if available, otherwise generate synthetic data."""
    os.makedirs('data', exist_ok=True)
    preferred = 'data/food_supply_data.csv'
    fallback = 'data/food_supply_data_v2.csv'

    if os.path.exists(preferred):
        df = pd.read_csv(preferred)
        if 'food_type_encoded' not in df.columns and 'food_type' in df.columns:
            df['food_type_encoded'] = df['food_type'].map(FOOD_TYPE_MAP).fillna(0).astype(int)
        if 'risk_label' not in df.columns or 'loss_percentage' not in df.columns:
            df = generate_synthetic_dataset(6000)
    elif os.path.exists(fallback):
        df = pd.read_csv(fallback)
        if 'food_type_encoded' not in df.columns and 'food_type' in df.columns:
            df['food_type_encoded'] = df['food_type'].map(FOOD_TYPE_MAP).fillna(0).astype(int)
        if 'risk_label' not in df.columns or 'loss_percentage' not in df.columns:
            df = generate_synthetic_dataset(6000)
    else:
        df = generate_synthetic_dataset(6000)
        df.to_csv(preferred, index=False)
        print(f"[TRAIN] Generated dataset saved → {preferred}")
    return df


def train():
    os.makedirs('models', exist_ok=True)
    os.makedirs('data', exist_ok=True)

    df = load_dataset()
    print(f"[TRAIN] Training dataset loaded ({len(df)} rows)")

    required = ['temperature', 'humidity', 'rainfall', 'transit_time', 'storage_duration', 'food_type_encoded', 'risk_label']
    if not all(col in df.columns for col in required):
        print('[TRAIN] Dataset missing required columns, regenerating synthetic dataset.')
        df = generate_synthetic_dataset(6000)
        df.to_csv('data/food_supply_data.csv', index=False)

    features = ['temperature', 'humidity', 'rainfall', 'transit_time', 'storage_duration', 'food_type_encoded']
    X = df[features]
    y = df['risk_label']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )

    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(
        n_estimators=250,
        max_depth=18,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n[TRAIN] Model Performance Accuracy: {acc:.4f}\n")
    print(classification_report(y_test, y_pred, target_names=['Low', 'Moderate', 'High']))

    with open('models/model.pkl', 'wb') as f:
        pickle.dump(model, f)
    with open('models/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)

    print('[TRAIN] Model saved → models/model.pkl')
    print('[TRAIN] Scaler saved → models/scaler.pkl')
    return acc


if __name__ == '__main__':
    train()
