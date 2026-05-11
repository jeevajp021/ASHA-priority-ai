from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from datetime import datetime
from database import Base

class AshaWorker(Base):
    __tablename__ = "asha_workers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Sunita Devi")
    block = Column(String, default="Gondia")
    username = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=True)
    role = Column(String, default="ASHA")   # ASHA | SUPERVISOR | ADMIN

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    asha_id = Column(Integer, ForeignKey("asha_workers.id"))
    age = Column(Float)
    gestational_age = Column(Float)
    bp_systolic = Column(Float)
    bp_diastolic = Column(Float)
    haemoglobin = Column(Float)
    prev_hrp = Column(Integer, default=0)
    lat = Column(Float)
    lng = Column(Float)
    triage = Column(String, nullable=True)
    priority_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # ── A: New clinical fields ──────────────────────────────
    food_intake = Column(String, nullable=True)    # Good | Moderate | Poor
    glucose_level = Column(Float, nullable=True)   # mg/dL
    family_history = Column(Text, nullable=True)   # comma-separated: diabetes,hypertension,...
    # ── B: Workflow fields ──────────────────────────────────
    last_visit_date = Column(DateTime, nullable=True)
    next_visit_date = Column(DateTime, nullable=True)
    record_status = Column(String, default="ACTIVE")      # ACTIVE | FOLLOW_UP_REQUIRED | COMPLETED
    previous_triage = Column(String, nullable=True)        # tracks risk change

class Visit(Base):
    __tablename__ = "visits"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    asha_id = Column(Integer, ForeignKey("asha_workers.id"))
    lat = Column(Float)
    lng = Column(Float)
    visit_date = Column(DateTime, default=datetime.utcnow)

class Incentive(Base):
    __tablename__ = "incentives"
    id = Column(Integer, primary_key=True, index=True)
    asha_id = Column(Integer, ForeignKey("asha_workers.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    visit_id = Column(Integer, ForeignKey("visits.id"))
    amount = Column(Float, default=250.0)
    status = Column(String, default="PENDING")

# ── D: Audit log ────────────────────────────────────────────
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("asha_workers.id"))
    action = Column(String)           # VIEW_PATIENT | UPDATE_PATIENT | PREDICT | LOGIN
    patient_id = Column(Integer, nullable=True)
    detail = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)