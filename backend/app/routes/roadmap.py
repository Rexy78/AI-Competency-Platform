from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.models import User, Resume, LearningRoadmap
from app.utils.auth import get_current_user
from app.ai.llm_client import get_llm_client
from app.ai.prompts import ROADMAP_GENERATOR_PROMPT

router = APIRouter(prefix="/api/roadmap", tags=["Career Roadmap"])

@router.get("")
def get_user_roadmap(
    target_role: str = "Java Backend Developer",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if a saved roadmap exists for this target role
    roadmap_record = db.query(LearningRoadmap).filter(
        LearningRoadmap.user_id == current_user.id,
        LearningRoadmap.target_role == target_role
    ).order_by(LearningRoadmap.created_at.desc()).first()

    if roadmap_record and roadmap_record.steps_json:
        return {
            "target_role": target_role,
            "steps": roadmap_record.steps_json
        }

    # Generate personalized AI roadmap using Gemini API
    latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    current_skills = latest_resume.parsed_json.get("all_skills", []) if (latest_resume and latest_resume.parsed_json) else ["Java", "SQL", "Git", "HTML", "CSS"]

    steps = generate_gemini_roadmap(target_role, current_skills)

    new_record = LearningRoadmap(
        user_id=current_user.id,
        target_role=target_role,
        steps_json=steps
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return {
        "target_role": target_role,
        "steps": steps
    }

@router.post("/generate")
def generate_new_roadmap(
    target_role: str = Body("Java Backend Developer"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    current_skills = latest_resume.parsed_json.get("all_skills", []) if (latest_resume and latest_resume.parsed_json) else ["Java", "SQL", "Git", "HTML", "CSS"]

    steps = generate_gemini_roadmap(target_role, current_skills)

    new_record = LearningRoadmap(
        user_id=current_user.id,
        target_role=target_role,
        steps_json=steps
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return {
        "target_role": target_role,
        "steps": steps
    }

@router.post("/update")
def update_step_status(
    step_id: int = Body(...),
    status: str = Body(...),
    target_role: str = Body("Java Backend Developer"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    roadmap_record = db.query(LearningRoadmap).filter(
        LearningRoadmap.user_id == current_user.id,
        LearningRoadmap.target_role == target_role
    ).order_by(LearningRoadmap.created_at.desc()).first()

    if not roadmap_record:
        steps = generate_gemini_roadmap(target_role, [])
        roadmap_record = LearningRoadmap(
            user_id=current_user.id,
            target_role=target_role,
            steps_json=steps
        )
        db.add(roadmap_record)
        db.commit()
        db.refresh(roadmap_record)

    steps = list(roadmap_record.steps_json)
    for step in steps:
        if step.get("id") == step_id:
            step["status"] = status
            break

    roadmap_record.steps_json = steps
    db.commit()

    return {
        "message": "Roadmap progress updated",
        "steps": steps
    }

def generate_gemini_roadmap(target_role: str, current_skills: List[str]) -> List[Dict[str, Any]]:
    llm = get_llm_client()
    prompt = ROADMAP_GENERATOR_PROMPT.format(
        target_role=target_role,
        current_skills=", ".join(current_skills) if current_skills else "Basic programming",
        missing_skills="Containerization, Cloud Deployment, Frameworks"
    )

    try:
        data = llm.generate_json(prompt, system_prompt="You are an expert career architect.")
        if "steps" in data and isinstance(data["steps"], list) and len(data["steps"]) > 0:
            return data["steps"]
    except Exception as e:
        print("Gemini roadmap generation fallback:", e)

    # High-quality fallback structured roadmap with online platform recommendations
    return [
        {
            "id": 1,
            "skill": f"{target_role} Core Fundamentals",
            "category": "Core Engineering",
            "difficulty": "Beginner",
            "estimated_time": "2 Weeks",
            "priority": "High",
            "status": "Completed",
            "description": "Master core syntax, data structures, OOP patterns, and version control.",
            "prerequisites": ["Computer Science Basics"],
            "online_platforms": [
                {"platform": "Coursera", "title": "Software Engineering Specialization", "url": "https://www.coursera.org", "type": "Interactive Course"},
                {"platform": "YouTube / freeCodeCamp", "title": "Full Beginner Crash Course", "url": "https://www.youtube.com", "type": "Video Tutorial"},
                {"platform": "Official Documentation", "title": "Official Language Docs & Tutorials", "url": "https://developer.mozilla.org", "type": "Documentation"}
            ]
        },
        {
            "id": 2,
            "skill": "Backend Framework & REST API Architecture",
            "category": "Backend",
            "difficulty": "Intermediate",
            "estimated_time": "3 Weeks",
            "priority": "High",
            "status": "Learning",
            "description": "Build high-throughput RESTful web microservices and handle JSON data mapping.",
            "prerequisites": ["Core Fundamentals", "Git"],
            "online_platforms": [
                {"platform": "Udemy", "title": "Mastering Spring Boot & REST APIs", "url": "https://www.udemy.com", "type": "Paid Course"},
                {"platform": "GitHub Repositories", "title": "Awesome-Backend Microservice Templates", "url": "https://github.com", "type": "Code Template"},
                {"platform": "Postman Academy", "title": "REST API Design & Testing Certification", "url": "https://www.postman.com", "type": "Interactive Testing"}
            ]
        },
        {
            "id": 3,
            "skill": "Database Systems & ORM Persistence",
            "category": "Database",
            "difficulty": "Intermediate",
            "estimated_time": "2 Weeks",
            "priority": "High",
            "status": "Not Started",
            "description": "Design relational database schemas, write complex SQL joins, and optimize query indexing.",
            "prerequisites": ["REST APIs", "SQL Basics"],
            "online_platforms": [
                {"platform": "LeetCode / HackerRank", "title": "Top SQL Interview Database Challenges", "url": "https://leetcode.com", "type": "Coding Practice"},
                {"platform": "Coursera", "title": "Database Management Essentials (University of Colorado)", "url": "https://www.coursera.org", "type": "University Course"},
                {"platform": "PostgreSQL Official", "title": "PostgreSQL Tutorial & Indexing Manual", "url": "https://www.postgresql.org", "type": "Documentation"}
            ]
        },
        {
            "id": 4,
            "skill": "Docker Containerization & Microservices",
            "category": "DevOps",
            "difficulty": "Intermediate",
            "estimated_time": "2 Weeks",
            "priority": "Medium",
            "status": "Not Started",
            "description": "Package applications with Dockerfiles and orchestrate multi-container services via Docker Compose.",
            "prerequisites": ["Linux CLI", "REST APIs"],
            "online_platforms": [
                {"platform": "Docker Official Docs", "title": "Docker Getting Started Guide & CLI Reference", "url": "https://docs.docker.com", "type": "Official Manual"},
                {"platform": "freeCodeCamp", "title": "Docker for Beginners - Full Course", "url": "https://www.freecodecamp.org", "type": "Free Course"},
                {"platform": "Udemy", "title": "Docker & Kubernetes: The Practical Guide", "url": "https://www.udemy.com", "type": "Video Course"}
            ]
        },
        {
            "id": 5,
            "skill": "Cloud Infrastructure & CI/CD Deployment",
            "category": "Cloud",
            "difficulty": "Advanced",
            "estimated_time": "3 Weeks",
            "priority": "Medium",
            "status": "Not Started",
            "description": "Automate build and deployment pipelines using GitHub Actions onto AWS cloud infrastructure.",
            "prerequisites": ["Docker", "Git"],
            "online_platforms": [
                {"platform": "AWS Skill Builder", "title": "AWS Cloud Practitioner & Solutions Architect Essentials", "url": "https://aws.amazon.com", "type": "Cloud Training"},
                {"platform": "GitHub Skills", "title": "Automate workflows with GitHub Actions", "url": "https://skills.github.com", "type": "Hands-on Lab"},
                {"platform": "edX", "title": "Cloud Computing Fundamentals (IEEE / MIT)", "url": "https://www.edx.org", "type": "Academic Course"}
            ]
        }
    ]
