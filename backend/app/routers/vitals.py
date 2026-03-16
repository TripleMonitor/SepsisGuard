"""
Vitals submission and analysis API routes.
"""
from fastapi import APIRouter, HTTPException
from app.models import (
    Vitals, VitalsSubmission, VitalsRecord, AnalysisRequest,
    AnalysisResponse, AlertRecord,
)
from app.qsofa import calculate_qsofa, calculate_hybrid_risk
from app.gemini_agent import analyze_vitals_with_agent
from app.email_alerts import send_alert_email
from app.routers.patients import patients_db

router = APIRouter(prefix="/api", tags=["vitals"])

# Track alerts to avoid duplicates within a session
alert_history: list[AlertRecord] = []


@router.post("/patients/{patient_id}/vitals", response_model=AnalysisResponse)
async def submit_vitals(patient_id: str, data: VitalsSubmission):
    """
    Submit vitals for a patient.
    Computes qSOFA, runs AI analysis, and sends alerts if needed.
    """
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient = patients_db[patient_id]

    # Build Vitals model
    vitals = Vitals(
        heart_rate=data.heart_rate,
        spo2=data.spo2,
        temperature_f=data.temperature_f,
        respiratory_rate=data.respiratory_rate,
        systolic_bp=data.systolic_bp,
        gcs_score=data.gcs_score,
    )

    # Calculate qSOFA
    qsofa = calculate_qsofa(vitals)
    hybrid = calculate_hybrid_risk(vitals)

    # Store vitals record
    record = VitalsRecord(vitals=vitals, qsofa=qsofa)
    patient.vitals_history.append(record)

    # Run AI analysis
    try:
        explanation = await analyze_vitals_with_agent(vitals)
    except Exception as e:
        explanation = f"AI analysis unavailable: {str(e)}. qSOFA Score: {qsofa.score}/3 — {qsofa.risk_level} risk."

    # Send alerts if high risk
    alerts_sent = []
    if hybrid["alert"] and patient.emergency_contacts:
        alerts_sent = send_alert_email(
            patient_name=patient.name,
            patient_id=patient.id,
            vitals=vitals,
            qsofa=qsofa,
            contacts=patient.emergency_contacts,
        )
        alert_history.extend(alerts_sent)

    return AnalysisResponse(
        explanation=explanation,
        qsofa=qsofa,
        alert_sent=len(alerts_sent) > 0,
        alert_details=alerts_sent if alerts_sent else None,
        ml_score=hybrid["ml_score"],
        ml_risk_level=hybrid["risk_level"],
        recommendation=hybrid["recommendation"],
    )


@router.get("/patients/{patient_id}/vitals", response_model=list[VitalsRecord])
def get_vitals_history(patient_id: str):
    """Get vitals history for a patient."""
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patients_db[patient_id].vitals_history


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_vitals(data: AnalysisRequest):
    """
    Standalone analysis endpoint — analyze vitals without a patient record.
    Useful for quick checks.
    """
    qsofa = calculate_qsofa(data.vitals)
    hybrid = calculate_hybrid_risk(data.vitals)

    try:
        explanation = await analyze_vitals_with_agent(data.vitals)
    except Exception as e:
        explanation = f"AI analysis unavailable: {str(e)}. qSOFA Score: {qsofa.score}/3 — {qsofa.risk_level} risk."

    return AnalysisResponse(
        explanation=explanation,
        qsofa=qsofa,
        alert_sent=False,
        ml_score=hybrid["ml_score"],
        ml_risk_level=hybrid["risk_level"],
        recommendation=hybrid["recommendation"],
    )


@router.get("/alerts", response_model=list[AlertRecord])
def get_alert_history():
    """Get history of all alerts sent."""
    return alert_history
