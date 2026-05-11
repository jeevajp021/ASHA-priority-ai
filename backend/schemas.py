from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime

# ── Auth ─────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    role: str
    worker_id: int
    worker_name: str

# ── Patient ───────────────────────────────────────────────────
VALID_FOOD_INTAKE = {"Good", "Moderate", "Poor"}
VALID_FAMILY_HISTORY_TERMS = {"diabetes", "hypertension", "pregnancy_complications", "none"}

class PatientCreate(BaseModel):
    name: str
    asha_id: int = 1
    age: float
    gestational_age: float
    bp_systolic: float
    bp_diastolic: float
    haemoglobin: float
    prev_hrp: int = 0
    lat: float
    lng: float
    # New clinical fields — all optional for backward compat
    food_intake: Optional[str] = None
    glucose_level: Optional[float] = None
    family_history: Optional[str] = None   # comma-separated string
    next_visit_date: Optional[datetime] = None

    @field_validator("age", "gestational_age", "bp_systolic", "bp_diastolic", "haemoglobin")
    @classmethod
    def must_be_positive(cls, v, info):
        if v <= 0:
            raise ValueError(f"{info.field_name} must be a positive number")
        return v

    @field_validator("food_intake")
    @classmethod
    def valid_food_intake(cls, v):
        if v is not None and v not in VALID_FOOD_INTAKE:
            raise ValueError(f"food_intake must be one of {VALID_FOOD_INTAKE}")
        return v

    @field_validator("glucose_level")
    @classmethod
    def valid_glucose(cls, v):
        if v is not None and not (20.0 <= v <= 600.0):
            raise ValueError("glucose_level must be between 20 and 600 mg/dL")
        return v
    
class PatientOut(BaseModel):
    id: int
    name: str
    asha_id: int
    age: float
    gestational_age: float
    bp_systolic: float
    bp_diastolic: float
    haemoglobin: float
    prev_hrp: int
    lat: float
    lng: float

    triage: Optional[str] = None
    priority_score: Optional[float] = None
    record_status: Optional[str] = None

    class Config:
        from_attributes = True

class PatientFilter(BaseModel):
    triage: Optional[str] = None          # RED | YELLOW | GREEN
    record_status: Optional[str] = None   # ACTIVE | FOLLOW_UP_REQUIRED | COMPLETED
    asha_id: Optional[int] = None

class VisitCreate(BaseModel):
    patient_id: int
    asha_id: int = 1
    lat: float
    lng: float

class PredictRequest(BaseModel):
    patient_id: int