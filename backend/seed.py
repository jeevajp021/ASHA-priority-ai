"""Run once: python seed.py"""
from database import engine, SessionLocal, Base
import models

Base.metadata.create_all(bind=engine)
db = SessionLocal()

import bcrypt

def _hash(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

asha = models.AshaWorker(
    id=1, name="Sunita Devi", block="Gondia",
    username="sunita", password_hash=_hash("asha123"), role="ASHA"
)
db.merge(asha)

supervisor = models.AshaWorker(
    id=2, name="Dr. Meera Joshi", block="Gondia",
    username="supervisor", password_hash=_hash("super456"), role="SUPERVISOR"
)
db.merge(supervisor)

# Seed sample patients around Gondia, Maharashtra
patients_data = [
    dict(name="Meena Devi", asha_id=1, age=24, gestational_age=32, bp_systolic=150,
         bp_diastolic=95, haemoglobin=8.2, prev_hrp=1, lat=21.1458, lng=79.0882,
         food_intake="Poor", glucose_level=165, family_history="hypertension",
         record_status="FOLLOW_UP_REQUIRED"),
    dict(name="Priya Bai", asha_id=1, age=19, gestational_age=28, bp_systolic=110,
         bp_diastolic=70, haemoglobin=11.5, prev_hrp=0, lat=21.1502, lng=79.0945,
         food_intake="Moderate", glucose_level=95, family_history=None,
         record_status="ACTIVE"),
    dict(name="Savitri Rao", asha_id=1, age=32, gestational_age=36, bp_systolic=160,
         bp_diastolic=100, haemoglobin=7.8, prev_hrp=2, lat=21.1380, lng=79.0801,
         food_intake="Poor", glucose_level=210, family_history="diabetes,hypertension",
         record_status="FOLLOW_UP_REQUIRED"),
    dict(name="Kamla Singh", asha_id=1, age=28, gestational_age=20, bp_systolic=120,
         bp_diastolic=80, haemoglobin=10.2, prev_hrp=0, lat=21.1600, lng=79.1050,
         food_intake="Good", glucose_level=88, family_history=None,
         record_status="ACTIVE"),
    dict(name="Rukmini Netam", asha_id=1, age=22, gestational_age=38, bp_systolic=145,
         bp_diastolic=92, haemoglobin=9.1, prev_hrp=1, lat=21.1435, lng=79.0760,
         food_intake="Moderate", glucose_level=148, family_history="pregnancy_complications",
         record_status="ACTIVE"),
]

from engine.risk_model import predict_risk

for pd in patients_data:
    p = models.Patient(**pd)
    db.add(p)

db.commit()

# Run prediction on each seeded patient so triage is populated from startup
for p in db.query(models.Patient).all():
    result = predict_risk(p)
    p.triage = result["triage"]
    p.priority_score = result["priority_score"]

db.commit()

# Seed incentives
visits = []
for i, p in enumerate(db.query(models.Patient).all()):
    v = models.Visit(patient_id=p.id, asha_id=1, lat=p.lat, lng=p.lng)
    db.add(v)
    db.flush()
    status = ["PAID", "PENDING", "PROCESSING", "PAID", "PENDING"][i % 5]
    incentive = models.Incentive(asha_id=1, patient_id=p.id, visit_id=v.id, amount=250.0, status=status)
    db.add(incentive)

db.commit()
print("✅ Seed complete — 1 ASHA, 5 patients, visits & incentives loaded.")