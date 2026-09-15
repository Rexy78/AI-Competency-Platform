from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- Auth Schemas ---
class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Resume & Analysis Schemas ---
class PersonalInfo(BaseModel):
    name: Optional[str] = "Not Specified"
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None

class SkillCategoryBreakdown(BaseModel):
    programming_languages: List[str] = []
    frontend: List[str] = []
    backend: List[str] = []
    database: List[str] = []
    cloud_devops: List[str] = []
    data_ai: List[str] = []
    soft_skills: List[str] = []

class SectionExtraction(BaseModel):
    summary: Optional[str] = ""
    education: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    certifications: List[str] = []
    achievements: List[str] = []

class ResumeParsedData(BaseModel):
    personal_info: PersonalInfo
    sections: SectionExtraction
    skills_categorized: SkillCategoryBreakdown
    all_skills: List[str] = []

class SkillGapItem(BaseModel):
    skill: str
    category: str
    status: str # Available / Missing
    priority: str # High / Medium / Low

class SkillRecommendation(BaseModel):
    skill: str
    priority: str
    why: str
    prerequisites: List[str] = []
    next_steps: List[str] = []

class RoadmapStep(BaseModel):
    id: int
    skill: str
    category: str
    difficulty: str # Beginner, Intermediate, Advanced
    estimated_time: str # e.g. "2 Weeks"
    priority: str # High, Medium, Low
    status: str = "Not Started" # Not Started, Learning, Completed
    prerequisites: List[str] = []
    resources: List[str] = []

class JobMatchResult(BaseModel):
    role: str
    match_percentage: float
    matching_skills: List[str]
    missing_skills: List[str]
    description: Optional[str] = ""

class JDAnalysisRequest(BaseModel):
    job_description: str
    target_role: Optional[str] = None

class ResumeImprovementRequest(BaseModel):
    resume_id: Optional[int] = None
    target_role: Optional[str] = "Software Engineer"
    parsed_data: Optional[Dict[str, Any]] = None

class FeedbackCreate(BaseModel):
    rating: int
    comments: Optional[str] = ""
