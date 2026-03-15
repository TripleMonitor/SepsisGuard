"""
Pydantic models for the Sepsis Early Warning Agent.
Defines data structures for vitals, patients, qSOFA results, and API responses.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Vitals(BaseModel):
    """Patient vital signs input."""
    heart_rate: float = Field(..., ge=20, le=250, description="Heart rate in bpm")
    spo2: float = Field(..., ge=0, le=100, description="Blood oxygen saturation %")
    temperature_f: float = Field(..., ge=85, le=115, description="Temperature in °F")
    respiratory_rate: float = Field(..., ge=4, le=60, description="Breaths per minute")
    systolic_bp: float = Field(..., ge=40, le=300, description="Systolic blood pressure mmHg")
    gcs_score: int = Field(15, ge=3, le=15, description="Glasgow Coma Scale (3-15)")


class QSOFACriteria(BaseModel):
    """Individual qSOFA criteria evaluation."""
    respiratory_rate_elevated: bool = False
    systolic_bp_low: bool = False
    altered_mental_status: bool = False


class QSOFAResult(BaseModel):
    """qSOFA scoring result."""
    score: int = Field(..., ge=0, le=3)
    criteria: QSOFACriteria
    risk_level: str  # "low", "moderate", "high"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class VitalsRecord(BaseModel):
    """A vitals reading with computed qSOFA."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vitals: Vitals
    qsofa: QSOFAResult
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class EmergencyContact(BaseModel):
    """Emergency contact for a patient."""
    name: str
    email: str
    relationship: str = "Family"


class Patient(BaseModel):
    """Patient record."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    age: Optional[int] = None
    emergency_contacts: list[EmergencyContact] = []
    vitals_history: list[VitalsRecord] = []
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class PatientCreate(BaseModel):
    """Request body for creating a patient."""
    name: str
    age: Optional[int] = None
    emergency_contacts: list[EmergencyContact] = []


class VitalsSubmission(BaseModel):
    """Request body for submitting vitals."""
    heart_rate: float = Field(..., ge=20, le=250)
    spo2: float = Field(..., ge=0, le=100)
    temperature_f: float = Field(..., ge=85, le=115)
    respiratory_rate: float = Field(..., ge=4, le=60)
    systolic_bp: float = Field(..., ge=40, le=300)
    gcs_score: int = Field(15, ge=3, le=15)


class AnalysisRequest(BaseModel):
    """Request to analyze vitals with AI."""
    vitals: Vitals
    patient_name: str = "Patient"


class AlertRecord(BaseModel):
    """Record of an alert sent."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    patient_name: str
    contact_name: str
    contact_email: str
    qsofa_score: int
    message: str
    sent_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    success: bool = True


class AnalysisResponse(BaseModel):
    """Full response from vitals analysis."""
    explanation: str
    qsofa: QSOFAResult
    alert_sent: bool = False
    alert_details: Optional[list[AlertRecord]] = None
