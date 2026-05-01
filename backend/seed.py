from pydantic import BaseModel
from typing import Optional

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

class VisitCreate(BaseModel):
    patient_id: int
    asha_id: int = 1
    lat: float
    lng: float

class PredictRequest(BaseModel):
    patient_id: int