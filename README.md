# SIH26044 — Real AI-Powered Skill Intelligence & Matching Platform

[![Build Status](https://img.shields.io/badge/Build-Passing-emerald)](https://github.com/)
[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-teal)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)](https://sqlalchemy.org)
[![Smart India Hackathon](https://img.shields.io/badge/SIH-2026-orange)](https://sih.gov.in)

> **"We don't just tell students what jobs exist."**  
> We understand what students know $\to$ how strong they actually are $\to$ what skills industry needs $\to$ where the gaps are $\to$ what training should happen $\to$ whether students improved $\to$ which candidates match which opportunities $\to$ who gets hired $\to$ what the national skill ecosystem needs next.

---

## 🏛️ Platform Architecture Overview

The platform connects **4 Stakeholder Portals** through a unified **Central Skill Intelligence Engine**:

1. **Student Portal**: Skill profiles, resume skill extraction (PDF/text), $+ \text{Add Skill}$, evidence-aware proficiency breakdown ($S = w_T T + w_P P + w_V V + w_C C$), adaptive assessments, skill gap analysis against target careers, and AI-matched job applications.
2. **Recruiter Portal**: Company profile & multi-signal verification (🟢 Verified, 🟡 Verification Required, 🔴 Suspicious), job posting with dynamic **Skill Requirement Matrices** (Critical/High/Medium weights), AI candidate ranking with **"Why is Candidate ranked #X?"** explainability, and interview pipeline scheduler.
3. **Institution / TPO Portal**: Institutional telemetry, student roster & filterable skill directory, **Bulk Student Account Generator**, **Institution-Wide Skill Gap Heatmap**, targeted workshop creator, and **Measured Training Effectiveness Tracker** ($+ \Delta$ improvement points).
4. **Admin / Ministry Portal**: National Skill Intelligence Dashboard, **National Skill Supply vs Industry Demand Matrix**, **Platform Readiness Score ($PRS$) Leaderboard**, fake job / company verification audits, Government Opportunities & Apprenticeships Aggregator, and **National Hackathon Manager** (SIH 2026).
5. **AI Skill Intelligence Assistant**: Cross-portal natural language assistant that queries real database telemetry, drives frontend navigation, explains scores, and prepares confirmed actions.

---

## 📐 Core Mathematical Formats & Engines

### 1. Evidence-Aware Student Skill Proficiency Formula
$$S = w_T T + w_P P + w_V V + w_C C$$
* $T$: Adaptive Assessment Test Score (Weight: $0.40$)
* $P$: Practical Projects / Labs Score (Weight: $0.30$)
* $V$: Verified Experience / Resume Score (Weight: $0.15$)
* $C$: Coursework / Certifications Score (Weight: $0.15$)

#### Dynamic Missing Evidence Normalization
If single components are absent (e.g. no certification), weights are dynamically normalized over available non-null evidence:
$$w'_i = \frac{w_i}{\sum_{k \in \text{Available}} w_k}$$
This prevents penalizing students with zeros for missing single categories.

---

### 2. Explainable AI Candidate & Job Matching Engine
Evaluates candidate proficiencies against Recruiter Skill Requirement Matrices with importance weighting:
* **Critical**: Weight $3.0\times$
* **High**: Weight $2.0\times$
* **Medium**: Weight $1.0\times$

$$M = \left( \frac{\sum (f_i \times w_i)}{\sum w_i} \times 100 \times \text{eligibility\_factor} \right) + \text{project\_bonus} + \text{cert\_bonus}$$
where $f_i = \min\left(1.0, \frac{\text{Student Proficiency}}{R_i}\right)$.

---

### 3. Institutional Platform Readiness Score ($PRS$)
$$PRS = 0.35S + 0.25P + 0.20I + 0.10T + 0.10A$$
* $S$: Average verified skill proficiency across students
* $P$: Placement performance rate
* $I$: Internship participation rate
* $T$: Training / workshop completion rate
* $A$: Industry alignment index with national skill demand

---

## 🚀 Quick Start Guide

### Prerequisites
* Python 3.10+ (Tested on Python 3.13)
* Dependencies installed: `fastapi`, `uvicorn`, `sqlalchemy`, `pypdf`, `rapidfuzz`, `pyjwt`, `pytest`

### Running the Application (One Command)
```bash
python run.py
```
Open your browser at: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🔑 Demo Personas & Credentials

For presentation convenience, 1-click demo persona buttons are provided in the top header. You can also log in directly:

| Role | Demo Email | Password | Persona & Focus |
| :--- | :--- | :--- | :--- |
| **Student** | `student@sih.gov.in` | `Student@123` | **Rahul Sharma** (Pre-final year Dravyaguna scholar, NIA Jaipur, 8.95 CGPA) |
| **Recruiter** | `recruiter@dabur.com` | `Recruiter@123` | **Priya Menon** (Head of AYUSH Pharmaceutical Quality, Dabur AYUSH Life Sciences) |
| **Institution** | `tpo@nia.edu.in` | `Institution@123` | **Prof. S. Ranganathan** (TPO, National Institute of Ayurveda, Jaipur) |
| **Ministry / Admin** | `admin@ministry.gov.in` | `Admin@123` | **Dr. V. K. Saraswat** (National AYUSH Skill Council) |

---

## 🧪 Running the Automated Test Suite

```bash
pytest -v
```
Runs the full suite of unit and integration tests covering auth, proficiency formulas, dynamic evidence normalization, matching matrices, gap analyzers, adaptive assessments, and API endpoints.

---

## 🌟 10 WOW Features Implemented

1. **Resume Skill Extraction & Verification**: Upload PDF/text $\to$ extract via PyPDF + RapidFuzz $\to$ student interactive checklist verification $\to$ auto-update profile.
2. **True T/P/V/C Skill Proficiency Engine**: Normalized weight distribution with evidence explanations.
3. **Adaptive Skill Assessment**: Timed, randomized question sequencing with live scoring and proficiency recalculation.
4. **Explainable AI Matching**: Recruiter sees match score + "Why is Rahul ranked #1?" breakdown.
5. **Institution-Wide Skill Gap Heatmap**: Multi-year matrix identifying institutional deficits.
6. **National Supply vs Demand Matrix**: Closed-loop balance highlighting national deficits (e.g. AYUSH Good Manufacturing Practice 37%, Automated Formulation Intelligence 54%).
7. **Multi-Signal Company Verification**: CIN + Corporate Domain + Hiring History + Placement audit framework.
8. **National Skill Intelligence Dashboard**: Ecosystem telemetry across all institutions and states.
9. **Automated Policy Recommendations & Targeted Workshops**: Heatmap/gap detection $\to$ launch targeted training $\to$ measured post-training delta ($+ \Delta$).
10. **Role-Aware AI Skill Intelligence Assistant**: Natural language assistant with platform navigation and confirmable action draft execution.

---

## 📂 Project Structure

```
The_Hexagon-SIH26044/
├── backend/
│   └── app/
│       ├── ai_engine/       # Central Skill Intelligence Engine
│       │   ├── proficiency_engine.py
│       │   ├── matching_engine.py
│       │   ├── gap_analyzer.py
│       │   ├── verification_engine.py
│       │   ├── readiness_engine.py
│       │   ├── analytics_engine.py
│       │   └── assistant_engine.py
│       ├── api/             # REST API Routers
│       │   ├── auth_router.py
│       │   ├── student_router.py
│       │   ├── recruiter_router.py
│       │   ├── institution_router.py
│       │   ├── admin_router.py
│       │   ├── assessment_router.py
│       │   ├── ai_assistant_router.py
│       │   └── notifications_router.py
│       ├── auth/            # JWT & RBAC Middleware
│       ├── database/        # SQLAlchemy Engine & Session
│       ├── models/          # 30+ SQLAlchemy Models
│       ├── schemas/         # Pydantic Schemas
│       ├── seed/            # Realistic Dataset Generator
│       ├── services/        # Resume Extractor & Bulk Generator
│       └── main.py          # FastAPI Application
├── frontend/
│   ├── css/
│   │   └── main.css         # Glassmorphic SaaS Design System
│   ├── js/
│   │   ├── api.js           # REST Client
│   │   ├── auth.js          # Auth & Demo Switcher
│   │   ├── charts.js        # Chart.js Visualizations
│   │   ├── student_portal.js
│   │   ├── recruiter_portal.js
│   │   ├── institution_portal.js
│   │   ├── admin_portal.js
│   │   ├── ai_assistant.js  # Floating AI Drawer
│   │   └── app.js           # Main Controller
│   └── index.html           # Single Page Application
├── tests/                   # Pytest Test Suites
├── run.py                   # Platform Launcher
└── README.md
```
