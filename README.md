<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:FF00FF,100:00FFFF&height=250&section=header&text=EduTrack&fontSize=90&fontAlignY=35&desc=Intelligent%20Academic%20Command%20Center&descAlignY=55&descSize=20&animation=twinkling" />
</div>

<p align="center">
  <a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.herokuapp.com?font=Inter&weight=800&size=24&pause=1000&color=FF00FF&center=true&vCenter=true&width=600&lines=Smart+QR+Attendance;AI-Powered+Analytics;Deterministic+Recovery+Planner;Premium+Dashboard+Experience" alt="Typing SVG" /></a>
</p>

<div align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Three.js-000000?style=for-the-badge&logo=threedotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/Ollama_AI-FF00FF?style=for-the-badge&logo=robot&logoColor=white" />
</div>

---

## 🚀 Overview

**EduTrack** is a premium, hackathon-winning college academic platform designed to revolutionize how students and faculty interact with attendance, schedules, and academic data. 

Built with a stunning **Neon & White Design System**, EduTrack abandons the outdated, clunky university portals of the past and introduces a blazing fast, AI-powered command center.

<div align="center">
  <img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/neon.png" width="100%" />
</div>

## ✨ Key Features

- 🎯 **Deterministic Recovery Planner**: Never guess your attendance again. Know exactly how many consecutive classes you need to attend (or can afford to miss) to hit your target percentage.
- 📱 **Smart QR Attendance**: Faculty can generate time-limited QR codes. Students scan them in real-time to securely log attendance. No more proxy attendance.
- 🤖 **Local AI Assistant**: Integrated securely with Ollama, the on-device AI can answer contextual questions about your specific academic performance.
- 🎨 **Premium Aesthetic**: Powered by a custom CSS variable design system featuring deep glassmorphism, Three.js 3D hero visualization, and high-contrast neon accents.

<div align="center">
  <img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/neon.png" width="100%" />
</div>

## 🛠️ Architecture

- **Backend**: Python / FastAPI
- **Database**: SQLite (Production-ready schemas)
- **Frontend**: HTML5, Vanilla JavaScript, CSS3 (Zero heavy UI frameworks)
- **3D Graphics**: Three.js
- **Authentication**: JWT-based secure auth and Role-Based Access Control (RBAC).

<div align="center">
  <img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/neon.png" width="100%" />
</div>

## 🚦 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/EduTrack.git
   cd EduTrack
   ```

2. **Start the Backend server**
   ```bash
   pip install -r backend/requirements.txt
   python -m uvicorn backend.app.main:app --reload --port 8000
   ```

3. **Serve the Frontend**
   If you aren't serving the frontend through FastAPI, run a simple HTTP server:
   ```bash
   cd frontend/public
   python -m http.server 8080
   ```

4. **Open the Application**
   Navigate to `http://localhost:8000` (FastAPI) or `http://localhost:8080` in your web browser.

<div align="center">
  <img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/neon.png" width="100%" />
</div>

## 🔒 Security & Privacy

EduTrack enforces strict RBAC. Registration automatically defaults to the `student` role. Administrative and Faculty accounts must be provisioned securely on the backend, preventing unauthorized elevation of privileges. Data never leaves your network thanks to the local AI integration.

## 🤝 Contribution

We welcome contributions! Please follow the steps below:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:FF00FF,100:00FFFF&height=100&section=footer" />
</div>
