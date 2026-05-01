import os
import pickle
import numpy as np
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "xgb_model.pkl"

def _get_features(patient) -> np.ndarray:
    """Extract feature vector from Patient ORM object."""
    # Normalise: BP>140/90 = danger, Hb<10 = anaemic, age<20 or >35 = risk
    bp_flag   = 1 if (patient.bp_systolic > 140 or patient.bp_diastolic > 90) else 0
    anemia    = 1 if patient.haemoglobin < 10 else 0
    age_risk  = 1 if (patient.age < 20 or patient.age > 35) else 0
    ga_risk   = 1 if patient.gestational_age > 34 else 0  # near term

    return np.array([[
        patient.age,
        patient.gestational_age,
        patient.bp_systolic,
        patient.bp_diastolic,
        patient.haemoglobin,
        patient.prev_hrp,
        bp_flag,
        anemia,
        age_risk,
        ga_risk,
    ]])

def _load_or_train_model():
    if MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return _train_and_save()

def _train_and_save():
    """Generate synthetic training data and train XGBoost."""
    import xgboost as xgb
    from sklearn.preprocessing import StandardScaler

    np.random.seed(42)
    N = 2000

    age            = np.random.uniform(18, 42, N)
    gest_age       = np.random.uniform(8, 40, N)
    bp_sys         = np.random.uniform(90, 180, N)
    bp_dia         = np.random.uniform(60, 120, N)
    hb             = np.random.uniform(6.5, 14.0, N)
    prev_hrp       = np.random.randint(0, 4, N).astype(float)
    bp_flag        = (bp_sys > 140).astype(float)
    anemia         = (hb < 10).astype(float)
    age_risk       = ((age < 20) | (age > 35)).astype(float)
    ga_risk        = (gest_age > 34).astype(float)

    X = np.column_stack([age, gest_age, bp_sys, bp_dia, hb, prev_hrp,
                         bp_flag, anemia, age_risk, ga_risk])

    # Label: high-risk if multiple danger flags
    risk_score = bp_flag + anemia + age_risk + (prev_hrp > 0).astype(float) + ga_risk
    y = (risk_score >= 2).astype(int)

    model = xgb.XGBClassifier(n_estimators=100, max_depth=4, random_state=42, eval_metric='logloss')
    model.fit(X, y)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"✅ XGBoost model trained and saved to {MODEL_PATH}")
    return model

_MODEL = None

def predict_risk(patient) -> dict:
    global _MODEL
    if _MODEL is None:
        _MODEL = _load_or_train_model()

    features = _get_features(patient)
    prob = float(_MODEL.predict_proba(features)[0][1])

    # Priority score = weighted composite (slide formula)
    w1, w2, w3 = 0.5, 0.3, 0.2
    R_clinical = 1.0 if (patient.bp_systolic > 140 or patient.haemoglobin < 9) else (prob * 0.7)
    R_history  = min(patient.prev_hrp / 3.0, 1.0)
    R_vuln     = 0.4 if (patient.age < 20 or patient.age > 35) else 0.1
    priority_score = (R_clinical * w1) + (R_history * w2) + (R_vuln * w3)

    if priority_score >= 0.55 or patient.bp_systolic > 160:
        triage = "RED"
    elif priority_score >= 0.30:
        triage = "YELLOW"
    else:
        triage = "GREEN"

    factors = []
    if patient.bp_systolic > 140: factors.append(f"High BP: {patient.bp_systolic}/{patient.bp_diastolic} mmHg")
    if patient.haemoglobin < 10:  factors.append(f"Anaemia: Hb {patient.haemoglobin} g/dL")
    if patient.prev_hrp > 0:      factors.append(f"Prev HRP: {patient.prev_hrp} pregnancy(ies)")
    if patient.age < 20:          factors.append(f"Adolescent mother: age {patient.age}")
    if patient.age > 35:          factors.append(f"Advanced maternal age: {patient.age}")
    if patient.gestational_age > 36: factors.append(f"Near term: GA {patient.gestational_age} weeks")

    return {
        "triage": triage,
        "priority_score": round(priority_score, 4),
        "ml_probability": round(prob, 4),
        "risk_factors": factors,
    }