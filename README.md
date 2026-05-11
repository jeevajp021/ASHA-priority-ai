# 🩺 ASHA-Priority AI

### Intelligent Decision-Support for Precision Maternal Healthcare

> Turning frontline health data into actionable decisions.

---

## 📌 Overview

**ASHA-Priority AI** is a decision-support system designed to assist ASHA workers in identifying high-risk pregnancies and optimizing their daily field visits.

Instead of acting as a data collection tool, this system enables **real-time prioritization and action planning** based on patient health data.

---

## 🎯 Problem Statement

* 49.4% of pregnancies in India have high-risk factors
* Only ~14% are actively tracked through existing systems
* ASHA workers face:

  * Delayed decision-making
  * Inefficient field routing
  * Lack of actionable insights

👉 The issue is not lack of data — it's lack of **decision intelligence at the last mile**

---

## 💡 Solution

ASHA-Priority AI transforms raw maternal health data into:

* **Risk classification (RED / YELLOW / GREEN)**
* **Optimized daily visit routes**
* **Structured visit tracking with incentive visibility**

---

## ⚙️ Phase 1 (Current Implementation)

> Focus: Core Decision Intelligence

### ✔ Features Implemented

### 🧠 Risk Prediction Engine
Evaluates:

- Blood pressure
- Haemoglobin levels
- Glucose levels
- Food intake behavior
- Family history
- Age and gestational stage
- Previous pregnancy history

Outputs:

- Priority Score
- Risk Category (RED / YELLOW / GREEN)
- Contributing Risk Factors

Built using:

- Hybrid scoring approach
  - Rule-based clinical prioritization
  - ML-assisted scoring using synthetic training data
- XGBoost (trained on synthetic data)
- Threshold-based clinical overrides for explainability and consistency

Additional Features:

- Explainable risk reasoning
- Deterministic scoring for demo consistency
- Risk change tracking

---

### 🗺 Smart Route Optimization
Prioritizes high-risk (RED) patients first.

Routing logic includes:

- Priority-aware triage sorting
- Priority score ordering within same triage
- Nearest Neighbor route optimization
- 2-opt local route refinement

Visualization Features:

- Numbered visit sequence
- Start and end route markers
- Ordered patient traversal display

Outputs:

- Ordered visit path
- Estimated travel distance
- Route sequence clarity for field workers

Current Limitation:

- Distance estimation is coordinate-based and does not yet use real-world road networks or live map routing APIs.

---

#### 💰 Incentive Tracking System

* Logs each visit
* Tracks incentive status:

  * PENDING / PROCESSING / PAID
* Provides visibility into compensation workflow

---

### 🗂 Patient Workflow & Data Management

Additional workflow-oriented healthcare features include:

- Patient visit history tracking
- Last visit and next follow-up scheduling
- Record status management
  - ACTIVE
  - FOLLOW_UP_REQUIRED
  - COMPLETED
- Risk progression tracking
- Search and filter support for patient management

The system is designed to simulate structured healthcare workflow management rather than functioning as a basic CRUD application.

---

### 🔐 Healthcare Data Protection Features

Since healthcare information is highly sensitive, the system incorporates foundational security and validation mechanisms suitable for a healthcare workflow prototype.

Implemented Features:

- Username/password authentication
- Password hashing using bcrypt
- Role-based access control
  - ASHA Worker
  - Supervisor
  - Admin
- Audit logging for patient access and updates
- Input validation and sanitization
- Sensitive data masking where appropriate

The objective is to demonstrate responsible healthcare data handling without introducing heavy enterprise infrastructure.

---

## 🚫 Scope Limitations (Phase 1)

The following are **not implemented in this prototype**:

* Voice-based input (Bhashini)
* IVR system (feature phone interaction)
* Government system integration (RCH / HMIS)
* Real-time payment processing (UPI / PFMS)
* Fully offline edge deployment

👉 These are planned for Phase 2

---

## 🚀 Phase 2 (Future Scope)

> Focus: Accessibility & Real-world Deployment

Additional planned enhancements:

- AI-assisted voice interaction
- IVR-based accessibility for feature phones
- OCR-assisted paper-to-digital workflows
- Real-world map routing integration
- Multi-domain ASHA healthcare support
  - Child care
  - Nutrition tracking
  - Community health monitoring

---

## 🏗️ System Architecture

```
Frontend (React + Vite)
        ↓
Backend API (FastAPI)
        ↓
Core Engine
  ├── Risk Model (XGBoost)
  └── Route Optimizer
        ↓
Database (SQLite)
```

---

## 🛠️ Tech Stack

### Frontend

* React 18
* Vite
* Tailwind CSS
* Leaflet.js (Map Visualization)

### Backend

* Python 3.11
* FastAPI
* SQLAlchemy
* Pydantic

### AI / Logic

* XGBoost
* NumPy
* Scikit-learn

### Database

* SQLite (for prototype)

---

## 📂 Project Structure

```
ASHA-priority-ai/
│
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── seed.py
│   └── engine/
│       ├── risk_model.py
│       └── route_optimizer.py
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── README.md
└── .gitignore
```

---

## ⚡ Getting Started

### 🔹 Prerequisites

* Python 3.10+
* Node.js (v18+ recommended)
* Git

---

## 🔧 Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed database
python seed.py

# Run server
uvicorn main:app --reload
```

👉 Backend runs at:
`http://localhost:8000`

---

## 💻 Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

👉 Frontend runs at:
`http://localhost:5173`

---

## 🔗 API Endpoints (Core)

| Endpoint               | Description             |
| ---------------------- | ----------------------- |
| `/api/patients`        | Create / fetch patients |
| `/api/predict`         | Risk prediction         |
| `/api/route/{id}`      | Get optimized route     |
| `/api/incentives/{id}` | View incentives         |

---

## 🧪 Demo Flow

1. Open the web app
2. Enter patient details
3. Click **"Assess Risk"**
4. View:

   * Risk classification (RED/YELLOW/GREEN)
   * Priority score
5. Navigate to dashboard:

   * View optimized route
6. Check incentive ledger

---

## 🎬 Demo Strategy

* Show high-risk patient detection
* Demonstrate route prioritization
* Highlight decision clarity (not complexity)

---

## 🧠 Key Insight

>The system does not replace clinical judgment.
>Instead, it acts as a decision-support layer that helps frontline healthcare workers prioritize field actions using structured clinical indicators, workflow intelligence, and explainable risk scoring.

---

## 📌 Scope Clarification

While ASHA workers manage multiple healthcare responsibilities including child care, nutrition, and disease monitoring, Phase 1 intentionally focuses on maternal healthcare.

This scoped approach enables:

- Deep and accurate prioritization
- Reliable workflow validation
- Clear demonstration of decision intelligence
- Reduced implementation complexity during initial prototyping

The architecture is intentionally designed to be extendable toward broader ASHA workflows in future phases.

---

## 📈 Future Vision

* Scale to district-level deployments
* Extend to TB, vaccination, and NCD tracking
* Integrate fully with national health infrastructure

---

## 👥 Team

* Frontend Development
* Backend API Development
* ML & Risk Engine
* System Integration & Demo

---

## 📄 License

This project is developed for academic and hackathon purposes.

---

## ⚠️ Disclaimer

This is a prototype system built for demonstration purposes.
It is not intended for direct clinical use.

---