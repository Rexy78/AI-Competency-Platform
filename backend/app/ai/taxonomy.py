# Comprehensive Skill Taxonomy & Categorization Rules

SKILL_TAXONOMY = {
    "Programming Languages": [
        "Java", "Python", "JavaScript", "TypeScript", "C++", "C#", "Go", "Golang", "Rust", "Ruby", 
        "PHP", "Swift", "Kotlin", "Scala", "R", "Dart", "C", "SQL", "HTML5", "CSS3"
    ],
    "Frontend": [
        "HTML", "CSS", "React", "React.js", "Angular", "Vue.js", "Vue", "Next.js", "Tailwind CSS", 
        "Tailwind", "Redux", "Bootstrap", "SASS", "LESS", "Webpack", "Vite", "TypeScript", 
        "jQuery", "Material UI", "Chakra UI"
    ],
    "Backend": [
        "Node.js", "Express", "Express.js", "Spring Boot", "Spring", "Django", "FastAPI", "Flask", 
        "ASP.NET", "Laravel", "GraphQL", "REST API", "RESTful APIs", "Microservices", "Hibernate", 
        "JPA", "Kafka", "RabbitMQ", "gRPC"
    ],
    "Database": [
        "MySQL", "MongoDB", "PostgreSQL", "Redis", "SQLite", "Oracle", "Cassandra", 
        "Elasticsearch", "Firebase", "DynamoDB", "MariaDB", "Supabase", "SQL Server"
    ],
    "Cloud / DevOps": [
        "AWS", "Amazon Web Services", "Azure", "GCP", "Google Cloud Platform", "Docker", 
        "Kubernetes", "GitHub Actions", "CI/CD", "Terraform", "Linux", "Nginx", "Jenkins", 
        "Ansible", "Git", "GitHub", "GitLab"
    ],
    "Data / AI": [
        "Machine Learning", "NLP", "Natural Language Processing", "TensorFlow", "PyTorch", 
        "Pandas", "NumPy", "Scikit-Learn", "Deep Learning", "Computer Vision", "OpenCV", 
        "Keras", "Data Analysis", "Data Science", "Scipy", "Matplotlib", "Seaborn"
    ],
    "Soft Skills": [
        "Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management", 
        "Critical Thinking", "Adaptability", "Agile", "Scrum", "Collaboration", "Analytical Thinking"
    ]
}

# Standard Role Requirements Matrix for Target Roles & Skill Gap Engine
JOB_ROLE_REQUIREMENTS = {
    "Java Backend Developer": {
        "required": ["Java", "OOP", "SQL", "Spring Boot", "REST API", "Hibernate", "Microservices", "Docker", "Git"],
        "category": "Backend",
        "description": "Designs and builds robust Java microservices and enterprise applications."
    },
    "Full Stack Developer": {
        "required": ["JavaScript", "React", "Node.js", "Express", "HTML", "CSS", "SQL", "MongoDB", "Git", "REST API"],
        "category": "Full Stack",
        "description": "Develops end-to-end web applications across client frontend and server backend."
    },
    "Frontend Developer": {
        "required": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Next.js", "Tailwind CSS", "Redux", "Git"],
        "category": "Frontend",
        "description": "Crafts beautiful, interactive user interfaces with modern web standards."
    },
    "Backend Developer": {
        "required": ["Python", "Node.js", "FastAPI", "SQL", "PostgreSQL", "Redis", "Docker", "REST API", "Git"],
        "category": "Backend",
        "description": "Architects high-performance API services and scalable database backends."
    },
    "Python Developer": {
        "required": ["Python", "Django", "FastAPI", "Flask", "SQL", "PostgreSQL", "Git", "Docker", "REST API"],
        "category": "Backend",
        "description": "Builds scalable backends, microservices, and automation scripts using Python."
    },
    "Data Analyst": {
        "required": ["Python", "SQL", "Pandas", "NumPy", "Data Analysis", "Matplotlib", "Seaborn", "Excel", "Communication"],
        "category": "Data",
        "description": "Transforms business data into actionable visual insights and metrics."
    },
    "Data Scientist": {
        "required": ["Python", "Machine Learning", "Pandas", "NumPy", "Scikit-Learn", "SQL", "Statistics", "Deep Learning"],
        "category": "Data",
        "description": "Trains predictive statistical models and algorithms using statistical methods."
    },
    "Machine Learning Engineer": {
        "required": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "NLP", "Scikit-Learn", "Docker", "Git", "FastAPI"],
        "category": "AI",
        "description": "Deploys machine learning models to production cloud infrastructure."
    },
    "AI Engineer": {
        "required": ["Python", "NLP", "Deep Learning", "PyTorch", "TensorFlow", "FastAPI", "OpenCV", "Docker", "Git"],
        "category": "AI",
        "description": "Integrates cutting-edge LLMs and computer vision solutions into SaaS tools."
    },
    "DevOps Engineer": {
        "required": ["Linux", "Docker", "Kubernetes", "AWS", "GitHub Actions", "CI/CD", "Terraform", "Python", "Git"],
        "category": "DevOps",
        "description": "Automates cloud deployment pipelines, monitoring, and container infrastructure."
    },
    "Cloud Engineer": {
        "required": ["AWS", "Azure", "Linux", "Docker", "Terraform", "Nginx", "Kubernetes", "Git", "Security"],
        "category": "Cloud",
        "description": "Architects secure and scalable multi-cloud infrastructure environments."
    },
    "Software Engineer": {
        "required": ["Data Structures", "Algorithms", "Java", "Python", "SQL", "Git", "OOP", "System Design", "Problem Solving"],
        "category": "General",
        "description": "Applies computer science fundamentals to solve engineering challenges."
    }
}

# Alias for RAG Engine & Job Matcher compatibility
JOB_ROLE_SKILL_MAP = JOB_ROLE_REQUIREMENTS

def categorize_skills(extracted_skills: list) -> dict:
    categorized = {
        "programming_languages": [],
        "frontend": [],
        "backend": [],
        "database": [],
        "cloud_devops": [],
        "data_ai": [],
        "soft_skills": []
    }
    
    cat_map = {
        "Programming Languages": "programming_languages",
        "Frontend": "frontend",
        "Backend": "backend",
        "Database": "database",
        "Cloud / DevOps": "cloud_devops",
        "Data / AI": "data_ai",
        "Soft Skills": "soft_skills"
    }

    lowered_map = {}
    for cat_name, skill_list in SKILL_TAXONOMY.items():
        key = cat_map[cat_name]
        for s in skill_list:
            lowered_map[s.lower()] = (key, s)

    for skill in extracted_skills:
        skill_clean = skill.strip()
        lowered = skill_clean.lower()
        if lowered in lowered_map:
            key, canonical_name = lowered_map[lowered]
            if canonical_name not in categorized[key]:
                categorized[key].append(canonical_name)
        else:
            if any(term in lowered for term in ["react", "html", "css", "vue", "angular", "tailwind"]):
                if skill_clean not in categorized["frontend"]: categorized["frontend"].append(skill_clean)
            elif any(term in lowered for term in ["node", "express", "spring", "django", "api"]):
                if skill_clean not in categorized["backend"]: categorized["backend"].append(skill_clean)
            elif any(term in lowered for term in ["sql", "mongo", "db", "redis"]):
                if skill_clean not in categorized["database"]: categorized["database"].append(skill_clean)
            elif any(term in lowered for term in ["aws", "azure", "docker", "cloud", "git"]):
                if skill_clean not in categorized["cloud_devops"]: categorized["cloud_devops"].append(skill_clean)
            elif any(term in lowered for term in ["ai", "learning", "model", "python", "data"]):
                if skill_clean not in categorized["data_ai"]: categorized["data_ai"].append(skill_clean)
            else:
                if skill_clean not in categorized["programming_languages"]: categorized["programming_languages"].append(skill_clean)

    return categorized
