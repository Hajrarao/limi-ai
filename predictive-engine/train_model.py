import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
import json

# Load data
df = pd.read_csv("sensor_data.csv")

FEATURES = [
    "voltage", "internal_temp", "usage_hours", "external_temp",
    "humidity", "load_percentage", "temp_diff",
    "voltage_deviation", "heat_load_index"
]

X = df[FEATURES]
y = df["failure"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train XGBoost
model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.05,
    scale_pos_weight=3,      # handles class imbalance
    use_label_encoder=False,
    eval_metric="logloss",
    random_state=42
)

model.fit(
    X_train_scaled, y_train,
    eval_set=[(X_test_scaled, y_test)],
    verbose=50
)

# Evaluate
y_pred = model.predict(X_test_scaled)
print("\n=== Classification Report ===")
print(classification_report(y_test, y_pred))
print("=== Confusion Matrix ===")
print(confusion_matrix(y_test, y_pred))

# Save model + scaler
joblib.dump(model, "xgb_model.joblib")
joblib.dump(scaler, "scaler.joblib")
joblib.dump(FEATURES, "features.joblib")
print("\nModel saved: xgb_model.joblib")