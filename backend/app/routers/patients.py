"""
Patient management API routes.
"""
from fastapi import APIRouter, HTTPException
from app.models import Patient, PatientCreate

router = APIRouter(prefix="/api/patients", tags=["patients"])

# In-memory patient store (replace with database in production)
patients_db: dict[str, Patient] = {}


@router.post("", response_model=Patient)
def create_patient(data: PatientCreate):
    """Register a new patient with emergency contacts."""
    patient = Patient(
        name=data.name,
        age=data.age,
        emergency_contacts=data.emergency_contacts,
    )
    patients_db[patient.id] = patient
    return patient


@router.get("", response_model=list[Patient])
def list_patients():
    """List all registered patients."""
    return list(patients_db.values())


@router.get("/{patient_id}", response_model=Patient)
def get_patient(patient_id: str):
    """Get a specific patient by ID."""
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patients_db[patient_id]


@router.delete("/{patient_id}")
def delete_patient(patient_id: str):
    """Remove a patient."""
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    del patients_db[patient_id]
    return {"message": "Patient deleted"}
