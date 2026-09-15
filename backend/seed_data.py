import os
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.models import User, Skill, JobRole, JobRoleSkill
from app.utils.auth import get_password_hash
from app.ai.taxonomy import SKILL_TAXONOMY, JOB_ROLE_REQUIREMENTS

def seed_database():
    print("Initializing Database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Admin User
        admin_email = "admin@resumeai.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin_user = User(
                full_name="Platform Admin",
                email=admin_email,
                hashed_password=get_password_hash("admin123"),
                is_admin=True
            )
            db.add(admin_user)
            print(f"Created default admin: {admin_email} / admin123")

        # 2. Seed Skills Taxonomy
        added_skills = set(s.name for s in db.query(Skill).all())
        for category_name, skills_list in SKILL_TAXONOMY.items():
            for skill_name in skills_list:
                if skill_name not in added_skills:
                    new_skill = Skill(
                        name=skill_name,
                        category=category_name,
                        priority_level="High" if skill_name in ["Java", "Python", "React", "Docker", "SQL"] else "Medium"
                    )
                    db.add(new_skill)
                    added_skills.add(skill_name)

        # 3. Seed Job Roles & Required Skills
        for role_title, role_data in JOB_ROLE_REQUIREMENTS.items():
            existing_role = db.query(JobRole).filter(JobRole.title == role_title).first()
            if not existing_role:
                new_role = JobRole(
                    title=role_title,
                    description=role_data.get("description", ""),
                    category=role_data.get("category", "Engineering")
                )
                db.add(new_role)
                db.flush()

                for req_skill in role_data.get("required", []):
                    db_role_skill = JobRoleSkill(
                        job_role_id=new_role.id,
                        skill_name=req_skill,
                        priority="High" if req_skill in role_data["required"][:3] else "Medium",
                        category=role_data.get("category", "Backend")
                    )
                    db.add(db_role_skill)

        db.commit()
        print("Database seeded successfully with skills and job role taxonomy!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
