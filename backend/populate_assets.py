import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

KNOWLEDGE_FILES = {
    "knowledge/devops/kubernetes.md": """# Kubernetes (K8s) & Container Orchestration

Kubernetes automates deployment, scaling, and management of containerized applications.

## Key Primitives
- Pods: Smallest deployable units wrapping one or more containers
- Deployments: Declarative updates for Pods with rolling updates and rollbacks
- Services: ClusterIP, NodePort, LoadBalancer for networking and load balancing
- Ingress: HTTP/HTTPS routing into cluster services
- ConfigMaps & Secrets: Decoupling configuration and sensitive data from image builds
- Namespaces: Virtual cluster separation for environments (dev, staging, prod)
""",

    "knowledge/devops/ci_cd.md": """# Continuous Integration & Continuous Deployment (CI/CD)

CI/CD bridges software development and IT operations through automated pipelines.

## Pipeline Stages
- Build: Compile code, install dependencies, linting, unit test execution
- Test: Integration tests, code coverage thresholds, security vulnerability scans (SAST/DAST)
- Package: Multi-stage Docker image build, semantic tagging, registry push (Docker Hub / ECR / GHCR)
- Deploy: Automated rollout to staging and production (GitHub Actions, GitLab CI, Jenkins, ArgoCD)
""",

    "knowledge/interview/interview_prep.md": """# Tech Interview Preparation Strategy

Comprehensive framework for acing technical and behavioral software engineering interviews.

## Core Pillars
1. Data Structures & Algorithms: Arrays, Hash Maps, Linked Lists, Trees, Graphs, Dynamic Programming
2. System Design: Scalability, Latency vs Throughput, CAP Theorem, Caching, Sharding, Load Balancing
3. Resume Project Deep-Dives: Architecture decisions, trade-offs, performance bottlenecks overcome
4. STAR Method for Behavioral: Situation, Task, Action, Result
""",

    "knowledge/interview/java_interview.md": """# Java Backend Technical Interview Questions

High-frequency questions asked in top Java / Spring Boot interviews:

## Concepts & Answers
- **ArrayList vs LinkedList**: ArrayList is backed by a dynamic array offering O(1) random access but O(N) worst-case insertion/deletion. LinkedList uses a doubly-linked list with O(1) node insertion/deletion once positioned, but O(N) traversal.
- **HashMap Internals**: Uses an array of buckets (Node/Entry). Collisions handled via linked lists; converts to Red-Black Tree in Java 8+ when bucket threshold exceeds TREEIFY_THRESHOLD (8) for O(log N) worst-case lookup.
- **Spring Boot Annotations**: `@SpringBootApplication` combines `@Configuration`, `@EnableAutoConfiguration`, `@ComponentScan`.
- **JPA N+1 Problem**: Occurs when fetching parent entities causes N additional select queries for lazy-loaded children. Solved using `JOIN FETCH`, `@EntityGraph`, or batch fetching (`@BatchSize`).
""",

    "knowledge/interview/system_design.md": """# System Design Fundamentals

Core principles for designing resilient, large-scale distributed systems:

## Key Topics
- Horizontal Scaling vs Vertical Scaling
- Load Balancing algorithms: Round Robin, Least Connections, Consistent Hashing
- Caching layers: CDN (Cloudflare), In-Memory (Redis, Memcached), Cache Invalidation strategies
- Database Scaling: Read Replicas, Sharding (range-based vs hash-based), Master-Slave replication
- Asynchronous Queues: RabbitMQ, Apache Kafka for decoupling and event-driven architectures
""",

    "knowledge/interview/behavioral.md": """# Behavioral Interview Mastery

Structured behavioral responses using the STAR method:

- **Situation**: Contextualize the challenge, project timeline, and team size.
- **Task**: Define your explicit responsibility and goal.
- **Action**: Explain the concrete technical, analytical, or interpersonal steps YOU took.
- **Result**: Quantify the impact (e.g., 'reduced API latency by 45%', 'onboarded 3 engineers').
""",

    "knowledge/career_paths/fullstack_developer.md": """# Full Stack Developer Career Path

Combines frontend user interfaces with robust backend business logic and databases.

## Recommended Tech Stack
- Frontend: React / Next.js, TypeScript, Tailwind CSS
- Backend: Node.js/Express or Python/FastAPI or Java/Spring Boot
- Database: PostgreSQL, MySQL, and Redis
- DevOps: Docker, GitHub Actions, AWS / Vercel
""",

    "knowledge/career_paths/python_developer.md": """# Python Backend & AI Developer Path

Focuses on scalable microservices, data processing pipelines, and GenAI integration.

## Key Competencies
- Advanced Python, FastAPI, Django, Asyncio, Pydantic
- Database management with SQLAlchemy and PostgreSQL
- GenAI & LLM orchestration with LangChain, LlamaIndex, Gemini API
- Cloud deployment with Docker, Celery, and Redis
""",

    "knowledge/career_paths/data_scientist.md": """# Data Scientist & ML Engineer Path

Transforms raw data into predictive intelligence and production AI models.

## Core Toolkit
- Statistics, Probability, Hypothesis Testing, A/B Testing
- Data Manipulation: Pandas, NumPy, SQL
- Machine Learning & Deep Learning: Scikit-Learn, PyTorch, XGBoost
- Model Deployment: FastAPI, Docker, MLflow, ONNX
""",

    "knowledge/career_paths/devops_engineer.md": """# DevOps & Cloud Platform Engineer Path

Bridges development and operations to maximize software delivery velocity and system reliability.

## Core Pillars
- Linux systems administration and Bash scripting
- Containerization & Orchestration: Docker, Kubernetes, Helm
- Infrastructure as Code (IaC): Terraform, Ansible
- Observability: Prometheus, Grafana, ELK Stack
"""
}

PROMPT_TEMPLATES = {
    "app/ai/prompts/system_prompt.txt": """You are Astra, an expert AI Career Assistant and Mentor.

Your purpose is to help candidates understand their resume, identify skill gaps, prepare for jobs, improve their resumes, and create personalized learning plans.

You have access to the candidate's analyzed resume and career profile.

Always personalize your response using the candidate context when relevant.
Do not invent information about the candidate.
If something is not present in the resume, clearly say that it is not available.
If the candidate asks about a technical concept, explain it clearly using beginner-friendly examples when appropriate.
If the candidate asks what they should learn, prioritize skills based on their target role and identified skill gaps.
If the candidate asks about their ATS score, explain the reasons behind the score using the available analysis.
Do not claim that the candidate has experience that is not present in their resume.
Do not generate fake achievements, companies, projects or experience.
When recommending a learning path, explain why each skill is useful.
You are a career guidance assistant, not a guaranteed job-placement system.
""",

    "app/ai/prompts/resume_context.txt": """Candidate Profile Context:
Name: {name}
Target Role: {target_role}
ATS Score: {ats_score}/100
Current Skills: {skills}
Missing Skills (Identified Gaps): {missing_skills}
Matching Skills: {matching_skills}
Education: {education}
Experience: {experience}
Projects: {projects}
""",

    "app/ai/prompts/career_prompt.txt": """Target Role: {target_role}
Candidate Skills: {skills}
Skill Gaps: {missing_skills}

Provide clear, structured, and highly actionable career guidance tailored strictly to this candidate's background and target role.
""",

    "app/ai/prompts/skill_gap_prompt.txt": """Target Role: {target_role}
Candidate Current Skills: {skills}
Identified Missing Skills: {missing_skills}

Analyze the skill gaps. Prioritize which skills to learn first, explain the technical reasons why each skill is crucial for this role, and outline prerequisites.
""",

    "app/ai/prompts/ats_prompt.txt": """Candidate ATS Score: {ats_score}/100
Matching Skills: {matching_skills}
Missing Keywords / Skills: {missing_skills}
Summary: {summary}

Explain why the candidate received this ATS score. Identify exact keywords missing from their resume, formatting risks, and concrete steps to increase their score.
""",

    "app/ai/prompts/interview_prompt.txt": """Target Role: {target_role}
Candidate Skills: {skills}
Candidate Projects: {projects}

You are conducting a Mock Technical Interview.
Ask a clear, relevant technical or architectural question tailored to the candidate's background and target role.
When evaluating an answer, provide:
1. Technical Accuracy (score out of 10)
2. Completeness (score out of 10)
3. Clarity (score out of 10)
4. Specific actionable feedback and an improved model answer.
""",

    "app/ai/prompts/chatbot_prompt.txt": """User Message: {user_message}

Relevant Candidate Context:
{candidate_context}

Relevant Knowledge Context:
{rag_context}

Conversation History:
{history}

Answer as Astra, an encouraging, professional, and precise AI Career Assistant.
"""
}

def populate():
    for rel_path, content in {**KNOWLEDGE_FILES, **PROMPT_TEMPLATES}.items():
        file_path = BASE_DIR / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"Created: {rel_path}")

if __name__ == "__main__":
    populate()
