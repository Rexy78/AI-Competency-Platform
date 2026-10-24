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


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_role = Column(String(150), nullable=False)
    job_description_id = Column(Integer, nullable=True)
    interview_type = Column(String(100), default="technical")
    difficulty = Column(String(50), default="intermediate")
    total_questions = Column(Integer, default=10)
    current_question = Column(Integer, default=1)
    status = Column(String(50), default="active")
    overall_score = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    session_data = Column(JSON, default=dict)

    user = relationship("User")
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    reports = relationship("InterviewReport", back_populates="session", cascade="all, delete-orphan")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    difficulty = Column(String(50), nullable=True)
    topic = Column(String(100), nullable=True)

    session = relationship("InterviewSession", back_populates="questions")
    answers = relationship("InterviewAnswer", back_populates="question", cascade="all, delete-orphan")


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    answer = Column(Text, nullable=False)
    score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    clarity_score = Column(Float, default=0.0)
    completeness_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("InterviewQuestion", back_populates="answers")


class InterviewPerformance(Base):
    __tablename__ = "interview_performance"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    topic = Column(String(100), nullable=False)
    score = Column(Float, default=0.0)
    questions_attempted = Column(Integer, default=0)
    strength_level = Column(String(50), default="moderate")


class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    overall_score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    problem_solving_score = Column(Float, default=0.0)
    role_readiness = Column(Float, default=0.0)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    learning_plan = Column(JSON, default=list)

    session = relationship("InterviewSession", back_populates="reports")


class PracticeAssessment(Base):
    __tablename__ = "practice_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(150), default="Placement Assessment")
    sections = Column(JSON, default=list)
    total_questions = Column(Integer, default=0)
    duration_minutes = Column(Integer, default=60)
    status = Column(String(50), default="active")
    score = Column(Float, default=0.0)
    readiness = Column(Float, default=0.0)
    result_json = Column(JSON, default=dict)
    questions_json = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class PracticeAnswer(Base):
    __tablename__ = "practice_answers"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("practice_assessments.id"), nullable=False)
    question_id = Column(String(100), nullable=False)
    question_category = Column(String(100), nullable=False)
    selected_option = Column(String(20), nullable=True)
    correct_option = Column(String(20), nullable=True)
    is_correct = Column(Boolean, default=False)
    marks = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class PracticeCodingProblem(Base):
    __tablename__ = "practice_coding_problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    topic = Column(String(100), nullable=False)
    difficulty = Column(String(50), default="Medium")
    description = Column(Text, nullable=False)
    input_format = Column(Text, nullable=True)
    output_format = Column(Text, nullable=True)
    constraints = Column(Text, nullable=True)
    example_input = Column(Text, nullable=True)
    example_output = Column(Text, nullable=True)
    template = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    public_test_cases = Column(JSON, default=list)
    hidden_test_cases = Column(JSON, default=list)
    time_limit_ms = Column(Integer, default=1000)
    memory_limit_mb = Column(Integer, default=256)
    supported_languages = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class PracticeCodingSubmission(Base):
    __tablename__ = "practice_coding_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("practice_coding_problems.id"), nullable=False)
    language = Column(String(50), default="Python")
    code = Column(Text, nullable=False)
    status = Column(String(50), default="pending")
    score = Column(Float, default=0.0)
    passed_cases = Column(Integer, default=0)
    total_cases = Column(Integer, default=0)
    execution_time_ms = Column(Integer, default=0)
    output = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)


class PracticeRecommendation(Base):
    __tablename__ = "practice_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PracticePerformance(Base):
    __tablename__ = "practice_performance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment_name = Column(String(150), nullable=False)
    overall_score = Column(Float, default=0.0)
    readiness = Column(Float, default=0.0)
    section_scores = Column(JSON, default=dict)
    coding_score = Column(Float, default=0.0)
    tests_completed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
