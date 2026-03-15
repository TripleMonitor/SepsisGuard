"""
qSOFA (Quick Sequential Organ Failure Assessment) Scoring Engine.

Criteria (1 point each):
  - Respiratory Rate >= 22 breaths/min
  - Systolic Blood Pressure <= 100 mmHg
  - Altered Mental Status (GCS < 15)

Score >= 2 indicates HIGH risk for sepsis-related mortality.
"""
from app.models import Vitals, QSOFACriteria, QSOFAResult


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
