import os
import pickle
import numpy as np
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "xgb_model.pkl"

def _get_features(patient) -> np.ndarray:
    """Extract feature vector from Patient ORM object."""
    bp_flag   = 1 if (patient.bp_systolic > 140 or patient.bp_diastolic > 90) else 0
    anemia    = 1 if patient.haemoglobin < 10 else 0
    age_risk  = 1 if (patient.age < 20 or patient.age >= 35) else 0
    ga_risk   = 1 if patient.gestational_age > 34 else 0

    # New clinical flags
    gluc_risk  = 1 if (patient.glucose_level or 0) > 140 else 0   # >140 mg/dL post-meal threshold
    poor_diet  = 1 if (patient.food_intake or "") == "Poor" else 0
    fam_hist   = 1 if _has_family_risk(patient.family_history) else 0

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
        gluc_risk,
        poor_diet,
        fam_hist,
    ]])

def _has_family_risk(family_history: str) -> bool:
    """Returns True if any high-risk term is in the comma-separated history string."""
    if not family_history:
        return False
    terms = {t.strip().lower() for t in family_history.split(",")}
    return bool(terms & {"diabetes", "hypertension", "pregnancy_complications"})

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
    age_risk       = ((age < 20) | (age >= 35)).astype(float)
    ga_risk        = (gest_age > 34).astype(float)

    # New synthetic features matching inference flags
    glucose        = np.random.uniform(70, 250, N)
    gluc_risk      = (glucose > 140).astype(float)
    poor_diet      = np.random.choice([0, 1], size=N, p=[0.7, 0.3]).astype(float)
    fam_hist       = np.random.choice([0, 1], size=N, p=[0.6, 0.4]).astype(float)

    X = np.column_stack([age, gest_age, bp_sys, bp_dia, hb, prev_hrp,
                         bp_flag, anemia, age_risk, ga_risk,
                         gluc_risk, poor_diet, fam_hist])

    # Label: high-risk if multiple danger flags (include new factors)
    risk_score = (bp_flag + anemia + age_risk + (prev_hrp > 0).astype(float)
                  + ga_risk + gluc_risk * 0.5 + poor_diet * 0.3 + fam_hist * 0.3)
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

    # Guard against obviously invalid inputs
    if patient.age is None or patient.age <= 0:
        raise ValueError(f"Invalid age: {patient.age}")
    if patient.haemoglobin is None or patient.haemoglobin <= 0:
        raise ValueError(f"Invalid haemoglobin: {patient.haemoglobin}")
    if patient.bp_systolic is None or patient.bp_systolic <= 0:
        raise ValueError(f"Invalid bp_systolic: {patient.bp_systolic}")

    features = _get_features(patient)
    prob = float(_MODEL.predict_proba(features)[0][1])

    # Priority score = weighted composite (slide formula)
    w1, w2, w3 = 0.5, 0.3, 0.2
    # New clinical modifiers — additive nudges, capped so they don't override core score
    glucose_mod = 0.08 if (patient.glucose_level or 0) > 140 else 0.0
    diet_mod    = 0.05 if (patient.food_intake or "") == "Poor" else 0.0
    fam_mod     = 0.05 if _has_family_risk(patient.family_history) else 0.0

    R_clinical = 1.0 if (patient.bp_systolic > 140 or patient.haemoglobin < 9) else (prob * 0.7)
    R_history  = min(patient.prev_hrp / 3.0, 1.0)
    R_vuln     = 0.4 if (patient.age < 20 or patient.age >= 35) else 0.1
    priority_score = min(
        (R_clinical * w1) + (R_history * w2) + (R_vuln * w3)
        + glucose_mod + diet_mod + fam_mod,
        1.0   # hard cap
    )

    if priority_score >= 0.55 or patient.bp_systolic > 160:
        triage = "RED"
    elif priority_score >= 0.30:
        triage = "YELLOW"
    else:
        triage = "GREEN"

    factors = []
    if patient.bp_systolic > 140:
        factors.append(f"High BP: {patient.bp_systolic}/{patient.bp_diastolic} mmHg")
    if patient.haemoglobin < 10:
        factors.append(f"Anaemia: Hb {patient.haemoglobin} g/dL")
    if patient.prev_hrp > 0:
        factors.append(f"Prev HRP: {patient.prev_hrp} pregnancy(ies)")
    if patient.age < 20:
        factors.append(f"Adolescent mother: age {int(patient.age)}")
    if patient.age >= 35:
        factors.append(f"Advanced maternal age: {int(patient.age)}")
    if patient.gestational_age > 36:
        factors.append(f"Near term: GA {patient.gestational_age} weeks")
    # New factor explanations
    if (patient.glucose_level or 0) > 140:
        factors.append(f"High glucose: {patient.glucose_level} mg/dL (threshold 140)")
    if (patient.food_intake or "") == "Poor":
        factors.append("Poor nutritional intake reported")
    if _has_family_risk(patient.family_history):
        terms = [t.strip() for t in (patient.family_history or "").split(",")]
        factors.append(f"Family history: {', '.join(terms)}")

    return {
        "triage": triage,
        "priority_score": round(priority_score, 4),
        "ml_probability": round(prob, 4),
        "risk_factors": factors,
    }