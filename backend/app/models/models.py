from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="owner", cascade="all, delete-orphan")
    analyses = relationship("ResumeAnalysis", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    raw_text = Column(Text, nullable=True)
    parsed_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="resumes")
    analyses = relationship("ResumeAnalysis", back_populates="resume", cascade="all, delete-orphan")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=False) # Programming, Frontend, Backend, Database, Cloud/DevOps, Data/AI, Soft Skills
    priority_level = Column(String(50), default="High") # High, Medium, Low

class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    skill_name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    proficiency = Column(String(50), default="Intermediate")

class JobRole(Base):
    __tablename__ = "job_roles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), default="Software Engineering")
    min_experience_years = Column(Integer, default=0)

    required_skills = relationship("JobRoleSkill", back_populates="job_role", cascade="all, delete-orphan")

class JobRoleSkill(Base):
    __tablename__ = "job_role_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_role_id = Column(Integer, ForeignKey("job_roles.id"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    priority = Column(String(50), default="High") # High, Medium, Low
    category = Column(String(100), default="Backend")

    job_role = relationship("JobRole", back_populates="required_skills")

class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_role = Column(String(150), nullable=True)
    ats_score = Column(Float, default=0.0)
    keyword_score = Column(Float, default=0.0)
    skills_score = Column(Float, default=0.0)
    formatting_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    section_completeness_score = Column(Float, default=0.0)
    suggestions_json = Column(JSON, nullable=True)
    radar_data_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="analyses")
    user = relationship("User", back_populates="analyses")
    skill_gaps = relationship("SkillGap", back_populates="analysis", cascade="all, delete-orphan")

class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("resume_analysis.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_role = Column(String(150), nullable=False)
    skill_name = Column(String(100), nullable=False)
    category = Column(String(100), default="General")
    status = Column(String(50), nullable=False) # Available / Missing
    priority = Column(String(50), default="Medium")

    analysis = relationship("ResumeAnalysis", back_populates="skill_gaps")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("resume_analysis.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    priority = Column(String(50), default="High")
    why_text = Column(Text, nullable=True)
    prerequisites_json = Column(JSON, nullable=True)
    next_steps_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, default=5)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedbacks")

class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_role = Column(String(150), nullable=False)
    steps_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id"), nullable=False)
    role = Column(String(50), nullable=False)  # user | assistant
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
