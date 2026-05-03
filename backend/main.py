from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime

import models, schemas
from database import engine, get_db, Base
from engine.risk_model import predict_risk
from engine.route_optimizer import optimize_route

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ASHA-Priority AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── PATIENTS ────────────────────────────────────────────

@app.get("/api/patients")
def list_patients(db: Session = Depends(get_db)):
    return db.query(models.Patient).all()

@app.post("/api/patients", status_code=201)
def create_patient(body: schemas.PatientCreate, db: Session = Depends(get_db)):
    patient = models.Patient(**body.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

@app.get("/api/patients/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return p

# ─── RISK PREDICTION ─────────────────────────────────────

@app.post("/api/predict")
def predict(body: schemas.PredictRequest, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == body.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    result = predict_risk(patient)

    patient.triage = result["triage"]
    patient.priority_score = result["priority_score"]
    db.commit()

    return result

# ─── VISITS ──────────────────────────────────────────────

@app.post("/api/visits", status_code=201)
def log_visit(body: schemas.VisitCreate, db: Session = Depends(get_db)):
    visit = models.Visit(**body.model_dump())
    db.add(visit)
    db.commit()
    db.refresh(visit)

    # Auto-create incentive record
    incentive = models.Incentive(
        asha_id=body.asha_id,
        patient_id=body.patient_id,
        visit_id=visit.id,
        amount=250.0,
        status="PENDING"
    )
    db.add(incentive)
    db.commit()
    return {"visit_id": visit.id, "incentive_created": True}

# ─── ROUTE OPTIMIZATION ──────────────────────────────────

@app.get("/api/route/{asha_id}")
def get_route(asha_id: int, db: Session = Depends(get_db)):
    patients = db.query(models.Patient).filter(
        models.Patient.asha_id == asha_id,
        models.Patient.lat != None
    ).all()

    if not patients:
        return {"route": [], "total_patients": 0, "estimated_minutes": 0}

    route = optimize_route(patients)
    return route

# ─── INCENTIVES ──────────────────────────────────────────

@app.get("/api/incentives/{asha_id}")
def get_incentives(asha_id: int, db: Session = Depends(get_db)):
    rows = db.query(models.Incentive, models.Patient, models.Visit).join(
        models.Patient, models.Incentive.patient_id == models.Patient.id
    ).join(
        models.Visit, models.Incentive.visit_id == models.Visit.id
    ).filter(models.Incentive.asha_id == asha_id).all()

    items = []
    total_pending = 0.0
    for incentive, patient, visit in rows:
        items.append({
            "patient_name": patient.name,
            "visit_date": str(visit.visit_date.date()) if visit and visit.visit_date else None,
            "amount": incentive.amount,
            "status": incentive.status,
        })
        if incentive.status == "PENDING":
            total_pending += incentive.amount

    return {"incentives": items, "total_pending": total_pending}

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ASHA-Priority AI"}