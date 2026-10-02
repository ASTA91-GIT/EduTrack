# EduTrack 📚✨

[![Demo Flow](file:///C:/Users/RAM/.gemini/antigravity-ide/brain/826484f8-fd89-492a-9295-e42b70ae0259/demo_flow_1790930031297.jpg)](file:///C:/Users/RAM/.gemini/antigravity-ide/brain/826484f8-fd89-492a-9295-e42b70ae0259/demo_flow_1790930031297.jpg)

## Overview
EduTrack is a **modern, AI‑enhanced attendance monitoring platform** designed for educational institutions. It provides real-time tracking, dynamic recovery planning, and a powerful local AI assistant for students.

**Built entirely locally**—zero cloud dependencies, no mock data, and full data privacy. PostgreSQL/SQLite serves as the single source of truth for all dashboards and analytics.

---

## Features
- **Secure Role-Based Dashboards:** Distinct interfaces for Students, Faculty, and Admins.
- **QR Code Attendance:** Faculty create dynamic QR sessions. Students scan to log attendance instantly, with server-side validation and duplicate prevention.
- **Attendance Recovery Planner:** Deterministic math engine calculates exactly how many future classes a student must attend (or can afford to miss) to maintain their required threshold.
- **What-If Simulator:** Allows students to test different attendance scenarios and see projected percentages.
- **Local AI Assistant (Ollama):** Chatbot embedded in the student dashboard that securely answers queries based *only* on the student's actual database context.
- **Analytics & Reporting:** Visual attendance trends and risk distribution charts.

---

## Architecture & Tech Stack
- **Backend:** FastAPI (Python), SQLAlchemy, JWT Authentication
- **Database:** PostgreSQL (with SQLite fallback for rapid development/testing)
- **Frontend:** Vanilla HTML, CSS (global design system), JavaScript (Fetch API)
- **Local AI:** Ollama running `llama3.2:1b` (or preferred model), isolated from database secrets via a strict context-injection bridge.

---

## Quick Start (Development)

### 1. Setup Backend
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r backend/app/requirements.txt
```

### 2. Environment Configuration
Copy the sample config and fill it out:
```bash
cp .env.example .env
```
Ensure you have the following keys in `.env`:
- `DATABASE_URL` (If empty, it falls back to `sqlite:///./edutrack.db`)
- `JWT_SECRET`
- `OLLAMA_BASE_URL=http://localhost:11434`
- `OLLAMA_MODEL=llama3.2:1b`

### 3. Seed Database & Run API
Populate the database with test data (admin, faculty, students, sessions, records):
```bash
python -m backend.scripts.seed
```

Start the FastAPI server:
```bash
uvicorn backend.app.main:app --reload
```

### 4. Open the App
The backend serves the frontend statically. Simply open:
**http://127.0.0.1:8000/** in your browser.

---

## Local AI Setup (Ollama)
For the "EduTrack AI" chatbot to work:
1. Install [Ollama](https://ollama.com/) locally.
2. Pull the required model:
   ```bash
   ollama pull llama3.2:1b
   ```
3. Run Ollama in the background:
   ```bash
   ollama serve
   ```

---

## Testing
EduTrack uses `pytest` for backend verification.
```bash
python -m pytest backend/tests/
```

---

## Security Highlights
- **No LLM Database Access:** The AI module only receives a sanitized JSON context of the authenticated student's attendance. It never executes SQL.
- **Role Guards:** Strict `require_teacher`, `require_student`, and admin checks on all API routes.
- **Zero LocalStorage Application Data:** All metrics, lists, and charts are fetched dynamically from the database. LocalStorage is exclusively used for JWT tokens.

---

*Built with love for hackathons – fast, beautiful, and fully functional.*
