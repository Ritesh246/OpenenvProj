from pydantic import BaseModel
from typing import List, Optional


class HospitalAction(BaseModel):
    action_type: str
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None


class HospitalObservation(BaseModel):
    waiting_patients: List[int]
    free_doctors: List[int]
    critical_patients: List[int]
    reward: float
    done: bool


class HospitalState(BaseModel):
    step_count: int
    total_patients: int
    treated_patients: int