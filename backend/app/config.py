import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "ResumeAI - AI Resume Analyzer, Builder & Career Assistant")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "resume_ai_super_secret_jwt_key_2026_change_in_production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/resume_ai_db")
    SQLITE_FALLBACK_URL: str = os.getenv("SQLITE_FALLBACK_URL", "sqlite:///./resume_ai.db")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    # Gemini / LLM settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")

settings = Settings()
