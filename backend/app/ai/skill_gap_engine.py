from typing import Dict, Any, List
from app.ai.taxonomy import JOB_ROLE_REQUIREMENTS, SKILL_TAXONOMY

def analyze_skill_gaps(user_skills: List[str], target_role: str = "Java Backend Developer") -> Dict[str, Any]:
    role_info = JOB_ROLE_REQUIREMENTS.get(target_role, JOB_ROLE_REQUIREMENTS["Java Backend Developer"])
    required_skills = role_info["required"]

    user_skills_lower = [s.lower().strip() for s in user_skills]

    gap_items = []
    matched_count = 0

    for req in required_skills:
        req_lower = req.lower().strip()
        is_matched = any(req_lower in s or s in req_lower for s in user_skills_lower)

        if is_matched:
            matched_count += 1
            status = "Available"
            priority = "—"
        else:
            status = "Missing"
            # High priority for core skills, medium/low for secondary
            if req in ["Java", "OOP", "Python", "JavaScript", "Spring Boot", "React", "Docker", "Machine Learning", "SQL"]:
                priority = "High"
            elif req in ["REST API", "Hibernate", "Microservices", "PostgreSQL", "AWS", "Kubernetes"]:
                priority = "Medium"
            else:
                priority = "Low"

        gap_items.append({
            "skill": req,
            "category": role_info.get("category", "Technical"),
            "status": status,
            "priority": priority
        })

    match_percentage = round((matched_count / len(required_skills)) * 100) if required_skills else 50

    # 6-Axis Radar Chart Data (Programming, Backend, Database, Cloud, DevOps, Soft Skills)
    categories = ["Programming", "Backend", "Database", "Cloud", "DevOps", "Soft Skills"]
    radar_data = []

    cat_skill_map = {
        "Programming": ["java", "python", "javascript", "c++", "sql"],
        "Backend": ["spring boot", "rest api", "hibernate", "express", "fastapi", "django"],
        "Database": ["mysql", "mongodb", "postgresql", "redis", "sql"],
        "Cloud": ["aws", "azure", "gcp", "cloud"],
        "DevOps": ["docker", "kubernetes", "git", "ci/cd", "linux"],
        "Soft Skills": ["communication", "problem solving", "leadership", "teamwork", "agile"]
    }

    for cat in categories:
        target_skills = cat_skill_map[cat]
        user_cat_score = sum(1 for s in user_skills_lower if any(t in s for t in target_skills))
        current_score = min(100, max(30, user_cat_score * 35))
        required_score = 85 if cat in ["Programming", "Backend", "Database"] else 75
        radar_data.append({
            "subject": cat,
            "A": current_score, # Candidate Current Score
            "B": required_score, # Target Benchmark Score
            "fullMark": 100
        })

    # Personalized Recommendations based on missing skills
    missing_skills = [item for item in gap_items if item["status"] == "Missing"]
    recommendations = []

    for item in missing_skills:
        skill_name = item["skill"]
        prio = item["priority"]
        
        if skill_name == "Spring Boot":
            why = "Spring Boot is one of the most in-demand frameworks for enterprise Java backend microservices."
            prereqs = ["Java", "OOP", "Collections", "Exception Handling"]
            next_steps = ["REST APIs", "Spring Data JPA", "Hibernate Integration"]
        elif skill_name == "Docker":
            why = "Docker is widely used to package, isolate, and deploy containerized microservices across cloud environments."
            prereqs = ["Linux Basics", "Command Line", "Networking Basics"]
            next_steps = ["Docker Compose", "Kubernetes", "CI/CD Pipelines"]
        elif skill_name == "REST API":
            why = "REST APIs form the backbone of modern frontend-backend communication and microservices architecture."
            prereqs = ["HTTP Basics", "JSON", "Backend Framework Basics"]
            next_steps = ["API Authentication", "Swagger/OpenAPI", "Postman Testing"]
        elif skill_name == "Hibernate":
            why = "Hibernate simplifies database operations through object-relational mapping (ORM) in enterprise Java applications."
            prereqs = ["SQL", "Java", "JDBC"]
            next_steps = ["Spring Data JPA", "Database Optimization", "Transaction Management"]
        else:
            why = f"{skill_name} is essential for closing key industry skill gaps and meeting benchmark role requirements."
            prereqs = ["Core Fundamentals", "Git"]
            next_steps = ["Practical Projects", "Certification / Documentation"]

        recommendations.append({
            "skill": skill_name,
            "priority": prio if prio != "—" else "Medium",
            "why": why,
            "prerequisites": prereqs,
            "next_steps": next_steps
        })

    # Learning Roadmap Generation
    roadmap_steps = generate_learning_roadmap(target_role, missing_skills)

    return {
        "target_role": target_role,
        "skill_match_percentage": match_percentage,
        "gap_matrix": gap_items,
        "radar_data": radar_data,
        "recommendations": recommendations,
        "roadmap": roadmap_steps
    }

def generate_learning_roadmap(target_role: str, missing_skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    role_info = JOB_ROLE_REQUIREMENTS.get(target_role, JOB_ROLE_REQUIREMENTS["Java Backend Developer"])
    all_role_skills = role_info["required"]

    default_roadmap_templates = {
        "Java Backend Developer": [
            {"skill": "Java Core & OOP", "category": "Programming", "difficulty": "Beginner", "time": "2 Weeks", "prio": "High"},
            {"skill": "Advanced Java & Collections", "category": "Programming", "difficulty": "Intermediate", "time": "2 Weeks", "prio": "High"},
            {"skill": "Spring Boot Fundamentals", "category": "Backend", "difficulty": "Intermediate", "time": "3 Weeks", "prio": "High"},
            {"skill": "RESTful Web APIs", "category": "Backend", "difficulty": "Intermediate", "time": "2 Weeks", "prio": "High"},
            {"skill": "Hibernate & JPA ORM", "category": "Database", "difficulty": "Intermediate", "time": "2 Weeks", "prio": "Medium"},
            {"skill": "Microservices Architecture", "category": "Backend", "difficulty": "Advanced", "time": "3 Weeks", "prio": "Medium"},
            {"skill": "Docker Containerization", "category": "DevOps", "difficulty": "Intermediate", "time": "2 Weeks", "prio": "Medium"},
            {"skill": "AWS Cloud Deployment", "category": "Cloud", "difficulty": "Advanced", "time": "3 Weeks", "prio": "Low"}
        ]
    }

    steps = default_roadmap_templates.get(target_role, [])
    if not steps:
        # Fallback dynamic step generation from required skills
        steps = []
        for i, sk in enumerate(all_role_skills):
            steps.append({
                "skill": sk,
                "category": "Technical",
                "difficulty": "Intermediate" if i > 2 else "Beginner",
                "time": f"{2 + (i % 2)} Weeks",
                "prio": "High" if i < 4 else "Medium"
            })

    roadmap_result = []
    for idx, item in enumerate(steps):
        roadmap_result.append({
            "id": idx + 1,
            "skill": item["skill"],
            "category": item["category"],
            "difficulty": item["difficulty"],
            "estimated_time": item["time"],
            "priority": item["prio"],
            "status": "Completed" if idx == 0 else ("Learning" if idx == 1 else "Not Started"),
            "prerequisites": [steps[idx-1]["skill"]] if idx > 0 else ["Fundamentals"],
            "resources": [
                f"Official {item['skill']} Documentation",
                f"Interactive {item['skill']} Hands-on Tutorial",
                f"Project-based {item['skill']} GitHub Repository"
            ]
        })

    return roadmap_result
