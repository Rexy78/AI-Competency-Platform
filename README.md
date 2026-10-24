# ResumeAnalyzer – AI Resume Analyzer, Builder & Career Assistant
![ResumeAnalyzer Platform](https://img.shields.io/badge/Stack-FastAPI%20%7C%20React%20%7C%20Tailwind%20%7C%20MySQL-6366f1?style=for-the-badge)

A full-stack, enterprise-grade AI career assistance platform designed to analyze resumes, calculate circular ATS scores, compute candidate skill gaps against 12+ benchmark tech roles, generate step-by-step learning roadmaps, recommend job fits, and build ATS-friendly resumes with live PDF export.

---

## 🌟 Key Features & Capabilities

### 1. 📄 Resume Parsing & ATS Intelligence
* **Multi-Format Extraction**: Parses `.pdf`, `.docx`, and `.txt` files automatically using PyMuPDF and python-docx.
* **0–100 ATS Score Meter**: Calculates compatibility based on Keyword Density, Skill Coverage, Formatting, Experience Relevance, and Section Completeness.
* **7-Category Skill Taxonomy Engine**: Categorizes candidate skills into:
  * *Programming Languages* (Java, Python, C++, JavaScript, TypeScript)
  * *Frontend Frameworks* (React, Vue, HTML, CSS, Tailwind)
  * *Backend & APIs* (Spring Boot, FastAPI, Node.js, Express, REST APIs)
  * *Databases* (MySQL, PostgreSQL, MongoDB, Redis)
  * *Cloud & DevOps* (AWS, Docker, Kubernetes, CI/CD, Git)
  * *Data Science & AI* (Pandas, NumPy, Machine Learning, spaCy)
  * *Soft Skills* (Agile, Problem Solving, Communication)

### 2. 🎯 Skill Gap & Career Radar Intelligence
* **Benchmark Role Comparison**: Evaluates profile against target roles (Java Backend, Full Stack, Frontend, Python, Data Scientist, DevOps, etc.).
* **Skill Gap Matrix**: Displays Available 🟢 vs Missing 🔴 skills with High/Medium/Low priority badges.
* **Interactive 6-Axis Radar Chart**: Compares Candidate vs Benchmark across Programming, Backend, Database, Cloud, DevOps, and Soft Skills using Recharts.
* **Personalized Recommendations**: Prioritized action items with prerequisites and next steps.

### 3. 🗺️ Step-by-Step Career Learning Roadmap
* **Sequential Skill Acquisition**: Structured progression path (e.g. Java → Spring Boot → REST APIs → Microservices → Docker → AWS).
* **Interactive Progress Tracker**: Live status updates (*Not Started*, *Learning*, *Completed*) persisted to database.
* **Learning Time & Difficulty**: Shows difficulty ratings, prerequisites, and curated documentation resources.

### 4. 💼 Job Matching & Targeted Job Description Analyzer
* **Job Role Recommendation**: Ranks matching positions with fit percentages, matching skills, missing skills, and path tips.
* **JD Tailoring Engine**: Paste raw job descriptions to extract required skills, experience, and receive specific resume tailoring recommendations.

### 5. ✍️ Resume Builder & AI Bullet Improver
* **4 Professional Templates**:
  1. *Professional* (Executive dark accents)
  2. *Modern* (Indigo gradient branding)
  3. *Minimal* (Clean typography and whitespace)
  4. *ATS Friendly* (Standard single-column format)
* **One-Click PDF Export**: Uses `html2pdf.js` for clean vector PDF downloads.
* **AI Bullet Point Enhancer**: Side-by-side *Before & After* rewrites using strong action verbs and quantifiable metrics without fake data.

### 6. 🛡️ Admin & Platform Management
* **Platform Analytics**: Total users, total resumes analyzed, average ATS scores.
* **User Directory**: View candidate accounts and registration dates.
* **Taxonomy Manager**: Live control panel to add new tech skills into the NLP taxonomy dictionary.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite, Tailwind CSS 3, Recharts, Lucide Icons, Axios, html2pdf.js |
| **Backend** | Python 3.9+, FastAPI, REST APIs, Pydantic, SQLAlchemy |
| **Database** | MySQL (with SQLite fallback support) |
| **Security** | JWT (JSON Web Tokens), Passlib (bcrypt password hashing) |
| **Document Processing** | PyMuPDF (fitz), python-docx |

---

## 📁 Project Architecture

```
Resume-Analyzer/
├── backend/
│   ├── app/
│   │   ├── ai/                      # AI & NLP Processing Core
│   │   │   ├── ats_scorer.py       # ATS scoring heuristics
│   │   │   ├── improver.py         # Bullet point & summary rewrites
│   │   │   ├── jd_analyzer.py      # Job description matcher
│   │   │   ├── job_matcher.py      # Role fit ranker
│   │   │   ├── parser.py           # PDF/DOCX parser
│   │   │   ├── skill_gap_engine.py # Skill gap & roadmap generator
│   │   │   └── taxonomy.py         # 7-Category skill taxonomy
│   │   ├── models/                 # SQLAlchemy Database Models
│   │   │   └── models.py
│   │   ├── routes/                 # FastAPI REST Endpoints
│   │   │   ├── admin.py
│   │   │   ├── auth.py
│   │   │   ├── dashboard.py
│   │   │   ├── jobs.py
│   │   │   ├── resume.py
│   │   │   ├── roadmap.py
│   │   │   └── skills.py
│   │   ├── utils/                  # Auth & Hashing Utils
│   │   │   └── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py                 # FastAPI Application Entry
│   ├── .env
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/            # Reusable UI Layouts & Navbar
│   │   │   ├── Footer.jsx
│   │   │   ├── Navbar.jsx
│   │   │   └── SidebarLayout.jsx
│   │   ├── context/               # Auth Context State
│   │   │   └── AuthContext.jsx
│   │   ├── pages/                 # Full Platform Views
│   │   │   ├── AdminDashboardPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── JDAnalyzerPage.jsx
│   │   │   ├── JobRecommendPage.jsx
│   │   │   ├── LandingPage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── ResumeAnalysisPage.jsx
│   │   │   ├── ResumeBuilderPage.jsx
│   │   │   ├── ResumeImprovementPage.jsx
│   │   │   ├── ResumeUploadPage.jsx
│   │   │   ├── RoadmapPage.jsx
│   │   │   ├── SignupPage.jsx
│   │   │   └── SkillGapPage.jsx
│   │   ├── services/              # Axios HTTP Service
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
└── schema.sql                      # MySQL DDL & Seed Data Script
```

---

## ⚡ Setup & Local Execution Guide

### 1. Backend Setup (FastAPI)
SQLite is used by default, so a separate database server is not required. To use MySQL instead, set `DATABASE_URL` in `backend/.env` to a valid MySQL connection URL and ensure the database and credentials are configured.

Install Python dependencies from the repository root:
   ```bash
   pip install -r backend/requirements.txt
   ```

### 3. Start the full application (FastAPI + React)
From the repository root, install frontend dependencies and start both servers:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   The backend runs at `http://localhost:8000` (API docs: `http://localhost:8000/docs`) and the frontend at `http://localhost:5174`. Stop the command with Ctrl+C to stop both.

   Install the backend dependencies before starting for the first time. The frontend proxies `/api` requests to `127.0.0.1:8000`, so the browser does not need a hard-coded localhost API URL. For a separately hosted production API, set `VITE_API_URL` to its origin; for a different local backend port, set `VITE_API_PROXY_TARGET` in the root `.env`.

---

---

## 🤖 AI Interview Preparation & Performance Analyzer

ResumeAnalyzer now includes an adaptive AI interview preparation module designed to behave like a real interview coach rather than a static list of canned questions.

### Core capabilities
* Resume-aware, role-aware interview planning
* Adaptive difficulty progression using AI-assisted evaluation
* Structured performance tracking per topic
* Weakness-practice mode focused on low-performing skills
* Final performance report with strengths, weaknesses, and learning plan
* Gemini backed answer evaluation and feedback generation
* LangGraph-style workflow orchestration for interview state progression

### Interview workflow
1. Candidate selects target role, interview type, and difficulty
2. AI planner analyzes resume, targets, and skill gaps
3. Question generator creates relevant, non-random interview questions
4. Candidate answers each question
5. Evaluation agent scores technical correctness, completeness, clarity, and relevance
6. Adaptive decision agent chooses the next question or weak-topic practice
7. Final report summarizes overall score, readiness, strengths, and recommendations

### API endpoints
* `POST /api/interview/start`
* `POST /api/interview/{session_id}/answer`
* `GET /api/interview/{session_id}/current-question`
* `GET /api/interview/{session_id}/performance`
* `GET /api/interview/{session_id}/report`
* `GET /api/interview/history`
* `POST /api/interview/{session_id}/finish`
* `POST /api/interview/weakness-practice`
* `POST /api/interview/{session_id}/retake`

### Environment variables
Create a `.env` based on `.env.example` and store the Gemini API key securely.

---

## 📜 License & Acknowledgments
Built with modern engineering standards for Final-Year CSE projects and career candidates.
