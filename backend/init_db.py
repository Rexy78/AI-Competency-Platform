import os
import sys
import pymysql

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import engine, Base
from app.models import models
from app.utils.auth import get_password_hash
from sqlalchemy.orm import Session

def init_database():
    print("--- Initializing ResumeAI MySQL Database ---")
    
    # 1. Parse MySQL host, port, user, password from DATABASE_URL
    # mysql+pymysql://root:password@localhost:3306/resume_ai_db
    db_url = settings.DATABASE_URL
    print(f"Connecting with database URL: {db_url}")

    # Extract connection params if MySQL
    if "mysql" in db_url:
        try:
            # Parse user, password, host, port
            url_parts = db_url.replace("mysql+pymysql://", "").split("@")
            user_pass = url_parts[0].split(":")
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            
            host_port_db = url_parts[1].split("/")
            host_port = host_port_db[0].split(":")
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 3306
            db_name = host_port_db[1] if len(host_port_db) > 1 else "resume_ai_db"

            print(f"Attempting to create database '{db_name}' on {host}:{port}...")
            connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password
            )
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4;")
            connection.commit()
            connection.close()
            print(f"Database '{db_name}' checked/created successfully!")
        except Exception as e:
            print(f"Notice during raw MySQL DB check: {e}")

    # 2. Create tables using SQLAlchemy
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

    # 3. Seed initial admin user if not exists
    with Session(engine) as session:
        admin_user = session.query(models.User).filter(models.User.email == "admin@resumeai.com").first()
        if not admin_user:
            admin_user = models.User(
                full_name="System Admin",
                email="admin@resumeai.com",
                hashed_password=get_password_hash("admin123"),
                is_admin=True
            )
            session.add(admin_user)
            session.commit()
            print("Seeded default Admin User: admin@resumeai.com / admin123")
        else:
            print("Admin user already exists.")

    print("--- Database Initialization Complete! ---")

if __name__ == "__main__":
    init_database()
