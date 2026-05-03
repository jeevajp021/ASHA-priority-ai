from pydantic import BaseModel, field_validator
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

    @field_validator("age", "gestational_age", "bp_systolic", "bp_diastolic", "haemoglobin")
    @classmethod
    def must_be_positive(cls, v, info):
        if v <= 0:
            raise ValueError(f"{info.field_name} must be a positive number")
        return v

class VisitCreate(BaseModel):
    patient_id: int
    asha_id: int = 1
    lat: float
    lng: float

class PredictRequest(BaseModel):
    patient_id: int