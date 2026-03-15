"""
Sepsis Early Warning Agent — FastAPI Application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import patients, vitals

app = FastAPI(
    title="Sepsis Early Warning Agent",
    description="AI-powered sepsis risk assessment using qSOFA scoring and Gemini AI",
    version="1.0.0",
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(patients.router)
app.include_router(vitals.router)


@app.get("/")
def root():
    return {
        "name": "Sepsis Early Warning Agent",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "patients": "/api/patients",
            "vitals": "/api/patients/{id}/vitals",
            "analyze": "/api/analyze",
            "alerts": "/api/alerts",
        }
    }
