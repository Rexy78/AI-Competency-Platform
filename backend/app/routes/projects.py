from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.models import User, Resume
from app.ai.llm_client import get_llm_client
from app.ai.prompts import PROJECT_GENERATOR_PROMPT

router = APIRouter(prefix="/api/projects", tags=["AI Project Generator"])

class ProjectGenRequest(BaseModel):
    target_role: Optional[str] = "Java Backend Developer"
    missing_skills: Optional[List[str]] = ["Spring Boot", "Docker", "REST API"]

@router.post("/generate")
def generate_project_blueprint(
    req: ProjectGenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    llm = get_llm_client()
    prompt = PROJECT_GENERATOR_PROMPT.format(
        target_role=req.target_role,
        missing_skills=", ".join(req.missing_skills) if req.missing_skills else "Spring Boot, Docker, REST API"
    )
    try:
        blueprint = llm.generate_json(prompt)
        return blueprint
    except Exception as e:
        return {
            "title": f"{req.target_role} Skill-Builder Microservice Platform",
            "objective": f"Develop a multi-tier production service to gain practical mastery in {', '.join(req.missing_skills)}.",
            "target_role": req.target_role,
            "technologies": req.missing_skills + ["MySQL", "Git"],
            "architecture": "Client UI / Postman -> API Gateway -> Business Logic Microservices -> Database Layer",
            "features": [
                "JWT Token-Based Authentication & Authorization",
                "Automated OpenAPI REST Documentation",
                "Containerization using multi-stage Dockerfiles"
            ],
            "skills_gained": req.missing_skills,
            "implementation_steps": [
                "Initialize project repository and configure environment variables",
                "Design database entities and repository access patterns",
                "Build REST endpoints and add robust error handling middleware",
                "Create Dockerfile & docker-compose.yml for local containerized deployment"
            ]
        }
