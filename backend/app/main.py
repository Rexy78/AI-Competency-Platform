from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routes import auth, resume, skills, jobs, roadmap, dashboard, admin, interview, projects, chatbot, chat
from seed_data import seed_database

# Create DB Tables on Startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full-Stack GenAI Resume Analyzer, Skill Gap Detector & Career Assistant API",
    version="1.0.0"
)

# Configure CORS for Frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed initial database
@app.on_event("startup")
def on_startup():
    seed_database()

# Register Routers
app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(skills.router)
app.include_router(jobs.router)
app.include_router(roadmap.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(interview.router)
app.include_router(projects.router)
app.include_router(chatbot.router)
app.include_router(chat.router)

@app.get("/")
def root_endpoint():
    return {
        "status": "online",
        "app_name": settings.PROJECT_NAME,
        "docs": "/docs"
    }
