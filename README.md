# ResumeAI – AI Resume Analyzer, Builder & Career Assistant

![ResumeAI Platform](https://img.shields.io/badge/Stack-FastAPI%20%7C%20React%20%7C%20Tailwind%20%7C%20MySQL-6366f1?style=for-the-badge)

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

### 1. Database Setup (MySQL)
Execute `schema.sql` in your MySQL server instance to create the database and seed taxonomy data.

**In PowerShell:**
```powershell
Get-Content schema.sql | mysql -u root -p
```
*or using CMD:*
```cmd
mysql -u root -p < schema.sql
```

### 2. Backend Setup (FastAPI)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the FastAPI backend server:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
   *The backend server will be live at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.*

### 3. Frontend Setup (React + Vite)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Launch the Vite development server:
   ```bash
   npm run dev
   ```
   *The web application will be accessible at `http://localhost:5173`.*

---

## 🔑 Demo Account Credentials

| Account Role | Email Address | Password |
| :--- | :--- | :--- |
| **System Administrator** | `admin@resumeai.com` | `admin123` |
| **Demo Candidate** | `alex.developer@example.com` | `alex123` |

---

## 📜 License & Acknowledgments
Built with modern engineering standards for Final-Year CSE projects and career candidates.
