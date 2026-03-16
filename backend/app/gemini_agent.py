"""
Gemini AI Agent for clinical vitals analysis.

Uses the Function Calling pattern from llm-app-patterns:
  - Register clinical tools as callable functions
  - Gemini decides which tools to invoke
  - Returns plain-language explanation of vitals
"""
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from app.models import Vitals
from app.qsofa import calculate_qsofa, get_risk_description, calculate_hybrid_risk

load_dotenv()


def _get_client():
    """Initialize Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in environment")
    return genai.Client(api_key=api_key)


# ── Tool definitions (Function Calling pattern) ──────────────────────────

def analyze_vital_signs(
    heart_rate: float,
    spo2: float,
    temperature_f: float,
    respiratory_rate: float,
    systolic_bp: float,
) -> dict:
    """Analyze individual vital signs and return their clinical significance."""
    analysis = {}

    # Heart Rate
    if heart_rate < 60:
        analysis["heart_rate"] = {"value": heart_rate, "status": "LOW (Bradycardia)", "concern": "high"}
    elif heart_rate > 100:
        analysis["heart_rate"] = {"value": heart_rate, "status": "HIGH (Tachycardia)", "concern": "high"}
    else:
        analysis["heart_rate"] = {"value": heart_rate, "status": "Normal", "concern": "none"}

    # SpO2
    if spo2 < 90:
        analysis["spo2"] = {"value": spo2, "status": "CRITICAL — Severe hypoxemia", "concern": "critical"}
    elif spo2 < 94:
        analysis["spo2"] = {"value": spo2, "status": "LOW — Hypoxemia", "concern": "high"}
    else:
        analysis["spo2"] = {"value": spo2, "status": "Normal", "concern": "none"}

    # Temperature
    if temperature_f > 100.4:
        analysis["temperature"] = {"value": temperature_f, "status": "FEVER", "concern": "high"}
    elif temperature_f < 96.8:
        analysis["temperature"] = {"value": temperature_f, "status": "LOW (Hypothermia)", "concern": "high"}
    else:
        analysis["temperature"] = {"value": temperature_f, "status": "Normal", "concern": "none"}

    # Respiratory Rate
    if respiratory_rate >= 22:
        analysis["respiratory_rate"] = {"value": respiratory_rate, "status": "ELEVATED (qSOFA criterion)", "concern": "high"}
    elif respiratory_rate < 12:
        analysis["respiratory_rate"] = {"value": respiratory_rate, "status": "LOW (Bradypnea)", "concern": "high"}
    else:
        analysis["respiratory_rate"] = {"value": respiratory_rate, "status": "Normal", "concern": "none"}

    # Systolic BP
    if systolic_bp <= 100:
        analysis["systolic_bp"] = {"value": systolic_bp, "status": "LOW / Hypotension (qSOFA criterion)", "concern": "high"}
    elif systolic_bp > 180:
        analysis["systolic_bp"] = {"value": systolic_bp, "status": "CRITICAL — Hypertensive crisis", "concern": "critical"}
    else:
        analysis["systolic_bp"] = {"value": systolic_bp, "status": "Normal", "concern": "none"}

    return analysis


def interpret_qsofa_score(
    score: int,
    respiratory_rate_elevated: bool,
    systolic_bp_low: bool,
    altered_mental_status: bool,
) -> dict:
    """Interpret qSOFA score and explain its clinical significance."""
    criteria_met = []
    if respiratory_rate_elevated:
        criteria_met.append("Respiratory Rate ≥ 22 breaths/min")
    if systolic_bp_low:
        criteria_met.append("Systolic Blood Pressure ≤ 100 mmHg")
    if altered_mental_status:
        criteria_met.append("Altered Mental Status (GCS < 15)")

    return {
        "score": score,
        "max_score": 3,
        "risk_description": get_risk_description(score),
        "criteria_met": criteria_met,
        "criteria_not_met_count": 3 - len(criteria_met),
        "requires_urgent_action": score >= 2,
    }


# ── Tool schemas for Gemini ──────────────────────────────────────────────

_tools = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="analyze_vital_signs",
                description="Analyze individual vital signs (heart rate, SpO2, temperature, respiratory rate, systolic BP) and return their clinical significance with normal/abnormal status.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "heart_rate": types.Schema(type="NUMBER", description="Heart rate in bpm"),
                        "spo2": types.Schema(type="NUMBER", description="Blood oxygen saturation percentage"),
                        "temperature_f": types.Schema(type="NUMBER", description="Body temperature in Fahrenheit"),
                        "respiratory_rate": types.Schema(type="NUMBER", description="Breaths per minute"),
                        "systolic_bp": types.Schema(type="NUMBER", description="Systolic blood pressure in mmHg"),
                    },
                    required=["heart_rate", "spo2", "temperature_f", "respiratory_rate", "systolic_bp"],
                ),
            ),
            types.FunctionDeclaration(
                name="interpret_qsofa_score",
                description="Interpret a qSOFA sepsis screening score and explain its clinical significance, which criteria are met, and whether urgent action is needed.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "score": types.Schema(type="INTEGER", description="qSOFA score (0-3)"),
                        "respiratory_rate_elevated": types.Schema(type="BOOLEAN", description="Whether respiratory rate >= 22"),
                        "systolic_bp_low": types.Schema(type="BOOLEAN", description="Whether systolic BP <= 100"),
                        "altered_mental_status": types.Schema(type="BOOLEAN", description="Whether GCS < 15"),
                    },
                    required=["score", "respiratory_rate_elevated", "systolic_bp_low", "altered_mental_status"],
                ),
            ),
        ]
    )
]

# ── Map function names to implementations ────────────────────────────────

_function_map = {
    "analyze_vital_signs": analyze_vital_signs,
    "interpret_qsofa_score": interpret_qsofa_score,
}


# ── Agent entry point ────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a Sepsis Early Warning AI Agent. Your role is to help patients' families 
understand vital signs and sepsis risk in clear, compassionate, non-medical language.

You have access to two clinical tools:
1. analyze_vital_signs — evaluates each vital sign individually
2. interpret_qsofa_score — interprets the qSOFA sepsis screening score

ALWAYS call BOTH tools to provide a complete analysis. After receiving the tool results, 
write a clear explanation that:
- Summarizes each vital sign in plain language (what it is, whether it's normal)
- Explains the qSOFA score and what it means for sepsis risk
- If risk is HIGH (score >= 2), clearly state this is urgent and medical help should be sought
- Use empathetic, non-technical language suitable for a worried family member
- Structure your response with clear sections using markdown headers

IMPORTANT: This is for educational/informational purposes only. Always advise consulting 
a healthcare professional for medical decisions."""


async def analyze_vitals_with_agent(vitals: Vitals) -> str:
    """
    Run the Gemini AI agent to analyze patient vitals.
    Uses the Function Calling pattern: Gemini decides which tools to call.
    """
    client = _get_client()

    # Compute qSOFA
    qsofa = calculate_qsofa(vitals)
    
    # Compute hybrid ML score
    hybrid = calculate_hybrid_risk(vitals)

    # Build user message with vital data
    user_message = f"""Please analyze the following patient vitals and provide a clear explanation:

- Heart Rate: {vitals.heart_rate} bpm
- Blood Oxygen (SpO2): {vitals.spo2}%
- Temperature: {vitals.temperature_f}°F
- Respiratory Rate: {vitals.respiratory_rate} breaths/min
- Systolic Blood Pressure: {vitals.systolic_bp} mmHg
- Glasgow Coma Scale (GCS): {vitals.gcs_score}/15

qSOFA Score: {qsofa.score}/3
- Respiratory Rate ≥ 22: {qsofa.criteria.respiratory_rate_elevated}
- Systolic BP ≤ 100: {qsofa.criteria.systolic_bp_low}
- Altered Mental Status (GCS < 15): {qsofa.criteria.altered_mental_status}

ML Sepsis Risk Score: {hybrid['ml_score']} (0.0 = no risk, 1.0 = highest risk)
Combined Risk Level: {hybrid['risk_level'].upper()}
Clinical Recommendation: {hybrid['recommendation']}

Please call the analyze_vital_signs and interpret_qsofa_score tools, then explain everything in simple language."""

    messages = [
        types.Content(role="user", parts=[types.Part.from_text(text=user_message)])
    ]

    # First call — Gemini should request tool calls
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=_tools,
            temperature=0.3,
        ),
    )

    # Process function calls (Function Calling loop)
    max_iterations = 5
    for _ in range(max_iterations):
        # Check if the model wants to call functions
        function_calls = []
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    function_calls.append(part)

        if not function_calls:
            # No more function calls — extract final text
            break

        # Add model's response to message history
        messages.append(response.candidates[0].content)

        # Execute each function call and collect results
        function_response_parts = []
        for part in function_calls:
            fn_name = part.function_call.name
            fn_args = dict(part.function_call.args) if part.function_call.args else {}

            # Execute the tool
            if fn_name in _function_map:
                result = _function_map[fn_name](**fn_args)
            else:
                result = {"error": f"Unknown function: {fn_name}"}

            function_response_parts.append(
                types.Part.from_function_response(
                    name=fn_name,
                    response=result,
                )
            )

        # Send function results back to Gemini
        messages.append(types.Content(role="user", parts=function_response_parts))

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=_tools,
                temperature=0.3,
            ),
        )

    # Extract final text response
    if response.candidates and response.candidates[0].content.parts:
        text_parts = [p.text for p in response.candidates[0].content.parts if p.text]
        return "\n".join(text_parts)

    return "Unable to generate analysis. Please consult a healthcare professional."
