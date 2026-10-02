# EduTrack 📚✨

[![Demo Flow](file:///C:/Users/RAM/.gemini/antigravity-ide/brain/826484f8-fd89-492a-9295-e42b70ae0259/demo_flow_1790930031297.jpg)](file:///C:/Users/RAM/.gemini/antigravity-ide/brain/826484f8-fd89-492a-9295-e42b70ae0259/demo_flow_1790930031297.jpg)

---

## Overview
EduTrack is a **modern, AI‑enhanced attendance monitoring platform** for colleges. It provides:
- Secure role‑based logins (students, faculty, admin)
- QR‑code based attendance sessions with server‑side validation
- Real‑time dashboards with beautiful dark‑mode UI
- Attendance analytics, low‑attendance warnings, CSV export

The project is built with **FastAPI**, **PostgreSQL**, and a **vanilla‑JS frontend** using modern design patterns (glassmorphism, gradients, micro‑animations).

---

## Features
- **QR Attendance Sessions** – Faculty creates a session, a QR code is generated, students scan it, and attendance is recorded instantly.
- **Real‑time Updates** – Faculty dashboard updates automatically via polling (future WebSocket support).
- **Analytics & Risk Alerts** – Visual charts, attendance percentages, and automated low‑attendance warnings.
- **Export & Reporting** – Export attendance records to CSV for administrative purposes.
- **Responsive Design** – Works beautifully on desktop and mobile devices.

---

## Quick Start
```bash
# Clone the repo
git clone https://github.com/ASTA91-GIT/EduTrack.git
cd EduTrack

# Backend setup (Python 3.11+)
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r backend/app/requirements.txt

# Set environment variables (create a .env file)
cp .env.example .env
# edit .env with your DB URL and JWT secret

# Run the API
uvicorn backend/app/main:app --reload
```

Open `http://localhost:8000` in your browser. The frontend lives under `frontend/` and can be served with any static server (e.g., `npm run dev` if you use Vite).

---

## API Endpoints (selected)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/attendance_sessions` | Create a new attendance session (faculty only) |
| `GET`  | `/api/v1/attendance_sessions/session/{token}/qr` | Retrieve QR code PNG for a session |
| `POST` | `/api/v1/attendance_sessions/scan` | Student scans QR; validates and records attendance |
| `GET`  | `/api/v1/attendance_sessions/session/{token}` | Get session status and current attendees |
| `POST` | `/api/v1/attendance_sessions/close` | Close a session (faculty) |

---

## Contributing
We welcome contributions! Follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feat/awesome-feature`).
3. Ensure code follows existing style and runs `pytest`.
4. Open a pull request with a clear description.

---

## License
Distributed under the MIT License. See `LICENSE` for more information.

---

*Built with love for hackathons – fast, beautiful, and production‑ready.*
