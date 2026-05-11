from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import bcrypt

import models, schemas
from database import engine, get_db, Base
from engine.risk_model import predict_risk
from engine.route_optimizer import optimize_route
from auth import create_token, get_current_worker, require_role

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ASHA-Priority AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── PATIENTS ────────────────────────────────────────────

@app.get("/api/patients", response_model=list[schemas.PatientOut])
def list_patients(
    triage: Optional[str] = Query(None),
    record_status: Optional[str] = Query(None),
    worker: models.AshaWorker = Depends(get_current_worker),
    db: Session = Depends(get_db),
):
    q = db.query(models.Patient)
    # ASHA sees only own patients; SUPERVISOR/ADMIN see all
    if worker.role == "ASHA":
        q = q.filter(models.Patient.asha_id == worker.id)
    if triage:
        q = q.filter(models.Patient.triage == triage.upper())
    if record_status:
        q = q.filter(models.Patient.record_status == record_status.upper())
    patients = q.all()
    _audit(db, actor_id=worker.id, action="LIST_PATIENTS",
           detail=f"triage={triage} status={record_status}")
    return patients

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
def predict(
    body: schemas.PredictRequest,
    worker: models.AshaWorker = Depends(get_current_worker),
    db: Session = Depends(get_db),
):
    patient = db.query(models.Patient).filter(models.Patient.id == body.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    # ASHA can only predict for own patients
    if worker.role == "ASHA" and patient.asha_id != worker.id:
        raise HTTPException(status_code=403, detail="Not your patient")

    result = predict_risk(patient)

    # Track triage change before overwriting
    if patient.triage and patient.triage != result["triage"]:
        patient.previous_triage = patient.triage
    patient.triage = result["triage"]
    patient.priority_score = result["priority_score"]
    patient.last_visit_date = datetime.utcnow()
    # Auto-flag follow-up for RED/YELLOW
    if result["triage"] in ("RED", "YELLOW"):
        patient.record_status = "FOLLOW_UP_REQUIRED"
    db.commit()

    _audit(db, actor_id=worker.id, action="PREDICT",
           patient_id=patient.id,
           detail=f"triage={result['triage']} score={result['priority_score']}")
    return result

@app.patch("/api/patients/{patient_id}/status")
def update_patient_status(
    patient_id: int,
    record_status: str = Query(..., description="ACTIVE | FOLLOW_UP_REQUIRED | COMPLETED"),
    worker: models.AshaWorker = Depends(get_current_worker),
    db: Session = Depends(get_db),
):
    if record_status not in ("ACTIVE", "FOLLOW_UP_REQUIRED", "COMPLETED"):
        raise HTTPException(status_code=422, detail="Invalid record_status value")
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if worker.role == "ASHA" and patient.asha_id != worker.id:
        raise HTTPException(status_code=403, detail="Not your patient")

    old_status = patient.record_status
    patient.record_status = record_status
    db.commit()
    _audit(db, actor_id=worker.id, action="UPDATE_STATUS",
           patient_id=patient_id, detail=f"{old_status} → {record_status}")
    return {"patient_id": patient_id, "record_status": record_status}

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
        models.Patient.lat != None,
        models.Patient.triage != None          # only route scored patients
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

# ─── AUTH ────────────────────────────────────────────────────

@app.post("/api/login", response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    worker = db.query(models.AshaWorker).filter(
        models.AshaWorker.username == body.username
    ).first()
    if not worker or not worker.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not bcrypt.checkpw(body.password.encode(), worker.password_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    _audit(db, actor_id=worker.id, action="LOGIN", detail=f"Login from username={body.username}")
    return {
        "access_token": create_token(worker.id, worker.role),
        "role": worker.role,
        "worker_id": worker.id,
        "worker_name": worker.name,
    }

# ─── AUDIT HELPER ────────────────────────────────────────────

def _audit(db: Session, actor_id: int, action: str,
           patient_id: int = None, detail: str = None):
    db.add(models.AuditLog(
        actor_id=actor_id, action=action,
        patient_id=patient_id, detail=detail
    ))
    db.commit()

@app.get("/api/audit")
def get_audit_log(
    patient_id: Optional[int] = Query(None),
    worker: models.AshaWorker = Depends(require_role("SUPERVISOR", "ADMIN")),
    db: Session = Depends(get_db),
):
    q = db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc())
    if patient_id:
        q = q.filter(models.AuditLog.patient_id == patient_id)
    logs = q.limit(200).all()
    return [
        {
            "actor_id": l.actor_id,
            "action": l.action,
            "patient_id": l.patient_id,
            "detail": l.detail,
            "timestamp": l.timestamp.isoformat(),
        }
        for l in logs
    ]