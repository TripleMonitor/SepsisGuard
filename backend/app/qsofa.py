"""
qSOFA (Quick Sequential Organ Failure Assessment) Scoring Engine.

Criteria (1 point each):
  - Respiratory Rate >= 22 breaths/min
  - Systolic Blood Pressure <= 100 mmHg
  - Altered Mental Status (GCS < 15)

Score >= 2 indicates HIGH risk for sepsis-related mortality.
"""
import os
import joblib
import pandas as pd
from app.models import Vitals, QSOFACriteria, QSOFAResult


# Load ML model once at startup, cache it
MODEL_PATH = os.path.join(os.path.dirname(__file__), "sepsis_pipeline.pkl")
try:
    ml_model = joblib.load(MODEL_PATH)
except Exception:
    ml_model = None


def calculate_qsofa(vitals: Vitals) -> QSOFAResult:
    """Calculate qSOFA score from patient vitals."""

    criteria = QSOFACriteria(
        respiratory_rate_elevated=vitals.respiratory_rate >= 22,
        systolic_bp_low=vitals.systolic_bp <= 100,
        altered_mental_status=vitals.gcs_score < 15,
    )

    score = sum([
        criteria.respiratory_rate_elevated,
        criteria.systolic_bp_low,
        criteria.altered_mental_status,
    ])

    if score >= 2:
        risk_level = "high"
    elif score == 1:
        risk_level = "moderate"
    else:
        risk_level = "low"

    return QSOFAResult(
        score=score,
        criteria=criteria,
        risk_level=risk_level,
    )


def get_risk_description(score: int) -> str:
    """Get human-readable description of qSOFA risk level."""
    descriptions = {
        0: "Low risk — No qSOFA criteria met. Continue routine monitoring.",
        1: "Moderate risk — One qSOFA criterion met. Increased vigilance recommended.",
        2: "HIGH RISK — Two qSOFA criteria met. Suspect sepsis. Urgent clinical assessment needed.",
        3: "CRITICAL — All three qSOFA criteria met. Immediate medical intervention required.",
    }
    return descriptions.get(score, "Unknown score")


def _get_ml_score(vitals: Vitals) -> float:
    """Get ML risk score from patient vitals."""
    if ml_model is None:
        return 0.0
    
    try:
        df = pd.DataFrame([{
            "HR": vitals.heart_rate,
            "O2Sat": vitals.spo2,
            "SBP": vitals.systolic_bp,
            "Resp": vitals.respiratory_rate,
            "Age": getattr(vitals, "age", 65.0),
            "Gender": getattr(vitals, "gender", 1)
        }])
        
        proba = ml_model.predict_proba(df)
        return float(proba[0][1])
    except Exception:
        return 0.0


def calculate_hybrid_risk(vitals: Vitals) -> dict:
    """Combine ML and qSOFA risk scores."""
    qsofa = calculate_qsofa(vitals)
    ml_score = _get_ml_score(vitals)
    
    threshold = 0.5
    
    # ML >= threshold AND qSOFA >= 2 → "high", alert=True
    if ml_score >= threshold and qsofa.score >= 2:
        risk_level = "high"
        alert = True
        rec = "Critical: High risk indicated by both ML model and qSOFA."
    # ML >= threshold OR qSOFA >= 2 → "moderate", alert=False
    elif ml_score >= threshold or qsofa.score >= 2:
        risk_level = "moderate"
        alert = False
        rec = "Increased vigilance recommended: Elevated risk indicated by either ML model or qSOFA."
    # Neither → "low", alert=False
    else:
        risk_level = "low"
        alert = False
        rec = "Low risk indicated. Continue routine monitoring."
        
    return {
        "ml_score": round(ml_score, 3),
        "risk_level": risk_level,
        "alert": alert,
        "recommendation": rec
    }
