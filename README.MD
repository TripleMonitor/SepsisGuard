# 🚑 SepsisGuard AI
### Early Warning System · Powered by Gemini AI

An AI-powered sepsis early warning system that helps home caregivers monitor patient vitals in real time, assess sepsis risk using the clinically validated qSOFA scoring tool, and automatically alert emergency contacts when vitals reach dangerous levels.

> Built as a student project. Not intended for real medical use.

---

## 🎯 The Problem

Sepsis kills **270,000 Americans every year** and is the #1 cause of hospital deaths. Most cases start at home — a patient has an infection, it escalates fast, and by the time they reach the ER it's too late. Family caregivers have no tool to know when "sick" becomes "call 911 right now."

SepsisGuard fills that gap.

---

## 🏗️ Architecture

```
Vitals Input (manual or simulated)
        ↓
qSOFA Clinical Scoring Engine
        ↓
Gemini AI Risk Assessment
        ↓
Real-time Dashboard
        ↓
Email Alert → Emergency Contact
```

---

## ✨ Features

- **Real-time vitals monitoring** — Heart rate, SpO2, temperature, respiratory rate, systolic BP, GCS score
- **qSOFA scoring** — Clinically validated sepsis screening tool used by ER doctors
- **AI Clinical Analysis** — Gemini AI explains what the numbers mean in plain English for non-medical caregivers
- **Automatic email alerts** — Fires to emergency contacts when qSOFA score hits danger threshold
- **Simulation mode** — Vitals automatically deteriorate over 3 minutes to demonstrate the system
- **Manual mode** — Caregivers can input real vitals from a thermometer and pulse oximeter
- **Patient registration** — Register multiple patients with emergency contact information
- **Alert history** — Full log of all alerts sent with timestamps

---

## 🔬 Clinical Methodology

SepsisGuard uses the **qSOFA (Quick Sequential Organ Failure Assessment)** score, a validated clinical tool used in emergency departments worldwide.

### Scoring Criteria (1 point each):
| Criterion | Threshold |
|---|---|
| Respiratory Rate | ≥ 22 breaths/min |
| Systolic Blood Pressure | ≤ 100 mmHg |
| Altered Mental Status | GCS < 15 |

### Risk Levels:
| Score | Status | Action |
|---|---|---|
| 0-1 | ✅ Normal | Monitor at home |
| 2 | ⚠️ Warning | Contact doctor |
| 3+ | 🚨 High Risk | Call 911 immediately |

*Source: MDCalc qSOFA Score — mdcalc.com/calc/2654/qsofa-quick-sofa-score-sepsis*

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + FastAPI |
| Frontend | React + Vite + Tailwind CSS |
| AI Reasoning | Google Gemini 2.5 Flash API |
| Email Alerts | Gmail SMTP |
| Testing | Pytest (11 passing tests) |
| Deployment | Railway (backend) + Vercel (frontend) |

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/sepsisguard
cd sepsisguard
```

### 2. Set up the backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Configure environment variables
Create a `.env` file in `/backend`:
```
GEMINI_API_KEY=your_gemini_api_key
ALERT_EMAIL_FROM=your@gmail.com
ALERT_EMAIL_PASSWORD=your_app_password
ALERT_EMAIL_TO=caregiver@gmail.com
```

### 4. Start the backend
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 3001
```

### 5. Set up the frontend
```bash
cd frontend
npm install
npm run dev
```

### 6. Open the app
Navigate to `http://localhost:5173`

---

## 🔑 API Setup

### Gemini API Key
1. Go to **aistudio.google.com**
2. Sign in with Google
3. Click **Get API Key**
4. Create a new key and copy it
5. Paste it as `GEMINI_API_KEY` in your `.env`

### Gmail SMTP Setup
1. Go to **myaccount.google.com**
2. Click **Security**
3. Enable **2-Step Verification**
4. Search **"App Passwords"**
5. Generate a new app password — name it "SepsisGuard"
6. Copy the 16 character code
7. Paste it as `ALERT_EMAIL_PASSWORD` in your `.env`
8. Set `ALERT_EMAIL_FROM` to the Gmail you generated the password from
9. Set `ALERT_EMAIL_TO` to the email that should receive alerts

---

## 🧪 Testing

```bash
cd backend/tests
pytest test_qsofa.py -v
```

**11 tests covering:**
- Normal score (0) with all normal vitals
- Score escalation at each threshold
- All boundary conditions for each criterion
- Risk level classification

---

## 📁 Project Structure

```
SepsisGuard/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── patients.py
│   │   │   └── vitals.py
│   │   ├── gemini_agent.py
│   │   ├── qsofa.py
│   │   ├── email_alerts.py
│   │   ├── models.py
│   │   └── main.py
│   ├── tests/
│   │   └── test_qsofa.py
│   └── requirements.txt
└── frontend/
    ├── src/
    └── package.json
```

---

## 🔮 Future Improvements

- **Custom ML model** — Train XGBoost on MIMIC-III ICU dataset for data-driven risk prediction alongside qSOFA
- **Wearable integration** — Real-time vitals from Apple Watch or Bluetooth pulse oximeter via Web Bluetooth API
- **Multilingual support** — Alert emails and AI explanations in multiple languages for non-English speaking families
- **Hospital API integration** — Connect to EHR systems for automatic vitals import
- **Mobile app** — Native iOS/Android for push notifications instead of email

---

## ⚠️ Disclaimer

SepsisGuard is a project built for educational purposes. It is **not a medical device** and should **not replace professional medical care**. Always consult a qualified healthcare provider for medical decisions. If you believe someone is experiencing a medical emergency, call 911 immediately.

---

## 📚 References

- MDCalc qSOFA Score: mdcalc.com/calc/2654/qsofa-quick-sofa-score-sepsis
- CDC Sepsis Data: cdc.gov/sepsis