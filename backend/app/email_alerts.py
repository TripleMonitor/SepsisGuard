"""
Gmail SMTP Email Alert System.

Sends email alerts to emergency contacts when qSOFA score >= 2.
Uses Gmail SMTP with App Password authentication.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from app.models import Vitals, QSOFAResult, AlertRecord, EmergencyContact

load_dotenv()


def _get_smtp_config():
    """Load SMTP configuration from environment."""
    return {
        "email": os.getenv("SMTP_EMAIL"),
        "password": os.getenv("SMTP_APP_PASSWORD"),
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "587")),
    }


def _build_alert_html(patient_name: str, vitals: Vitals, qsofa: QSOFAResult) -> str:
    """Build a formatted HTML email for the sepsis alert."""
    criteria_items = []
    if qsofa.criteria.respiratory_rate_elevated:
        criteria_items.append(f"<li>⚠️ Respiratory Rate: <strong>{vitals.respiratory_rate} breaths/min</strong> (elevated, ≥22)</li>")
    if qsofa.criteria.systolic_bp_low:
        criteria_items.append(f"<li>⚠️ Systolic Blood Pressure: <strong>{vitals.systolic_bp} mmHg</strong> (low, ≤100)</li>")
    if qsofa.criteria.altered_mental_status:
        criteria_items.append(f"<li>⚠️ Altered Mental Status: <strong>GCS {vitals.gcs_score}/15</strong> (below normal)</li>")

    criteria_html = "\n".join(criteria_items) if criteria_items else "<li>No criteria met</li>"

    return f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; padding: 24px; border-radius: 12px 12px 0 0;">
            <h1 style="margin: 0; font-size: 22px;">🚨 Sepsis Risk Alert</h1>
            <p style="margin: 8px 0 0; opacity: 0.9;">Immediate attention may be required</p>
        </div>

        <div style="background: #fff; border: 1px solid #e5e7eb; padding: 24px; border-radius: 0 0 12px 12px;">
            <p style="font-size: 16px; color: #111;">
                <strong>{patient_name}</strong> has a <strong style="color: #dc2626;">qSOFA score of {qsofa.score}/3</strong>,
                indicating a <strong>high risk</strong> of sepsis-related complications.
            </p>

            <h2 style="color: #dc2626; font-size: 16px; margin-top: 20px;">Triggered Criteria:</h2>
            <ul style="color: #333; line-height: 1.8;">
                {criteria_html}
            </ul>

            <h2 style="color: #333; font-size: 16px; margin-top: 20px;">All Current Vitals:</h2>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <tr style="background: #f9fafb;">
                    <td style="padding: 8px 12px; border: 1px solid #e5e7eb;">Heart Rate</td>
                    <td style="padding: 8px 12px; border: 1px solid #e5e7eb;"><strong>{vitals.heart_rate} bpm</strong></td>
                </tr>
                <tr>
                    <td style="padding: 8px 12px; border: 1px solid #e5e7eb;">Blood Oxygen (SpO2)</td>
                    <td style="padding: 8px 12px; border: 1px solid #e5e7eb;"><strong>{vitals.spo2}%</strong></td>
                </tr>
                <tr style="background: #f9fafb;">
                    <td style="padding: 8px 12px; border: 1px solid #e5e7eb;">Temperature</td>
                    <td style="padding: 8px 12px; border: 1px solid #e5e7eb;"><strong>{vitals.temperature_f}°F</strong></td>
                </tr>
                <tr>
                    <td style="padding: 8px 12px; border: 1px solid #e5e7eb;">Respiratory Rate</td>
                    <td style="padding: 8px 12px; border: 1px solid #e5e7eb;"><strong>{vitals.respiratory_rate} breaths/min</strong></td>
                </tr>
                <tr style="background: #f9fafb;">
                    <td style="padding: 8px 12px; border: 1px solid #e5e7eb;">Systolic BP</td>
                    <td style="padding: 8px 12px; border: 1px solid #e5e7eb;"><strong>{vitals.systolic_bp} mmHg</strong></td>
                </tr>
                <tr>
                    <td style="padding: 8px 12px; border: 1px solid #e5e7eb;">GCS Score</td>
                    <td style="padding: 8px 12px; border: 1px solid #e5e7eb;"><strong>{vitals.gcs_score}/15</strong></td>
                </tr>
            </table>

            <div style="margin-top: 24px; padding: 16px; background: #fef2f2; border-left: 4px solid #dc2626; border-radius: 4px;">
                <p style="margin: 0; color: #991b1b; font-size: 14px;">
                    <strong>⚡ Action Recommended:</strong> Please contact the patient's healthcare provider immediately.
                    A qSOFA score ≥ 2 suggests a higher risk of poor outcomes related to sepsis.
                </p>
            </div>

            <p style="margin-top: 20px; font-size: 12px; color: #9ca3af;">
                This is an automated alert from the Sepsis Early Warning System.
                This tool is for informational purposes only and does not replace professional medical advice.
            </p>
        </div>
    </body>
    </html>
    """


def send_alert_email(
    patient_name: str,
    patient_id: str,
    vitals: Vitals,
    qsofa: QSOFAResult,
    contacts: list[EmergencyContact],
) -> list[AlertRecord]:
    """Send alert emails to all emergency contacts. Returns list of alert records."""
    config = _get_smtp_config()

    if not config["email"] or not config["password"]:
        print("⚠️  SMTP credentials not configured — skipping email alerts")
        return []

    alert_records = []
    html_body = _build_alert_html(patient_name, vitals, qsofa)

    for contact in contacts:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 SEPSIS ALERT: {patient_name} — qSOFA Score {qsofa.score}/3"
        msg["From"] = f"Sepsis Early Warning <{config['email']}>"
        msg["To"] = contact.email

        plain_text = (
            f"SEPSIS RISK ALERT for {patient_name}\n\n"
            f"qSOFA Score: {qsofa.score}/3 — {qsofa.risk_level.upper()} RISK\n\n"
            f"Heart Rate: {vitals.heart_rate} bpm\n"
            f"SpO2: {vitals.spo2}%\n"
            f"Temperature: {vitals.temperature_f}°F\n"
            f"Respiratory Rate: {vitals.respiratory_rate} breaths/min\n"
            f"Systolic BP: {vitals.systolic_bp} mmHg\n"
            f"GCS: {vitals.gcs_score}/15\n\n"
            f"Please contact the patient's healthcare provider immediately."
        )

        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        success = True
        try:
            with smtplib.SMTP(config["host"], config["port"]) as server:
                server.starttls()
                server.login(config["email"], config["password"])
                server.send_message(msg)
            print(f"✅ Alert email sent to {contact.name} ({contact.email})")
        except Exception as e:
            print(f"❌ Failed to send alert to {contact.email}: {e}")
            success = False

        alert_records.append(AlertRecord(
            patient_id=patient_id,
            patient_name=patient_name,
            contact_name=contact.name,
            contact_email=contact.email,
            qsofa_score=qsofa.score,
            message=f"qSOFA {qsofa.score}/3 — {qsofa.risk_level} risk",
            success=success,
        ))

    return alert_records
