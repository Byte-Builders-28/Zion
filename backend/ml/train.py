import pandas as pd
import numpy as np
import pickle, os
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from synthetic_data import generate_normal, generate_attack
from feature_extractor import FEATURES

def train():
    # Generate data
    normal = generate_normal(800)
    attack = generate_attack(200)
    df = pd.concat([normal, attack], ignore_index=True)

    X_normal = normal[FEATURES].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_normal)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,  # let it 5% anomalies in real traffic (testing )
        random_state=42
    )
    model.fit(X_scaled)

    # Save both model and scaler
    os.makedirs("models", exist_ok=True)
    with open("models/isolation_forest.pkl", "wb") as f:
        pickle.dump({"model": model, "scaler": scaler}, f)

    # Quick evaluation on full data
    X_all = df[FEATURES].values
    X_all_scaled = scaler.transform(X_all)
    scores = model.decision_function(X_all_scaled)  # more negative = more anomalous

    # Normalize to 0–1 risk score (1 = most suspicious)
    risk = 1 - (scores - scores.min()) / (scores.max() - scores.min())

    normal_risk = risk[:len(normal)].mean()
    attack_risk = risk[len(normal):].mean()
    print(f"Avg risk — normal: {normal_risk:.3f}  attack: {attack_risk:.3f}")
    print("Model saved to models/isolation_forest.pkl")

if __name__ == "__main__":
    train()