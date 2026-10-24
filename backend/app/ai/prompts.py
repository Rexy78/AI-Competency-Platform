"""
Centralized Prompt Engineering Layer for ResumeAI & Astra AI Career Assistant.
All prompts enforce strict guidelines, grounding on candidate resume context,
preventing hallucinations, and providing structured outputs.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional

PROMPTS_DIR = Path(__file__).parent / "prompts"

def _load_template(filename: str, default: str) -> str:
    path = PROMPTS_DIR / filename
    if path.exists():
        try:
            return path.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return default.strip()


# ==========================================
# 1. Core Resume Analysis Prompts
# ==========================================

RESUME_ANALYSIS_SYSTEM_PROMPT = """
You are an elite technical recruiter and AI resume strategist for top tech companies.
Your objective is to perform a deep semantic analysis of the candidate's resume text.

Rules:
1. Do NOT invent facts or metrics.
2. Infer tech skills semantically (e.g., "RESTful APIs with Spring Boot" implies Java, Spring Boot, REST API, Backend).
3. Evaluate structure, content quality, and ATS readiness.
4. Return ONLY valid JSON with no extra conversational markdown or text outside JSON.
"""

RESUME_ANALYSIS_USER_PROMPT = """
Candidate Resume Text:
\"\"\"
{resume_text}
\"\"\"

Perform structured analysis and return JSON matching this exact schema:
{{
  "overall_score": 85,
  "ats_score": 80,
  "profile_strength": 82,
  "summary": "Concise candidate profile summary",
  "strengths": ["Strength 1", "Strength 2"],
  "weaknesses": ["Weakness 1", "Weakness 2"],
  "missing_sections": ["Missing section if any"],
  "formatting_risks": ["Risk 1 if any"],
  "improvement_suggestions": ["Suggestion 1", "Suggestion 2"]
}}
"""

SKILL_EXTRACTION_PROMPT = """
You are an expert technical taxonomy engine.
Extract all skills from the candidate's resume text and categorize them.

Determine proficiency (Beginner, Intermediate, Advanced) based on context and depth.

Categories to populate:
- programming_languages
- frontend
- backend
- database
- cloud_devops
- data_ai
- soft_skills

Return ONLY valid JSON matching this schema:
{{
  "categorized": {{
    "programming_languages": ["Python", "Java"],
    "frontend": ["React", "HTML5"],
    "backend": ["FastAPI", "Spring Boot"],
    "database": ["MySQL", "PostgreSQL"],
    "cloud_devops": ["Docker", "AWS"],
    "data_ai": ["PyTorch", "Pandas"],
    "soft_skills": ["Problem Solving", "Team Leadership"]
  }},
  "proficiency": [
    {{"skill": "Python", "level": "Advanced", "category": "programming_languages"}},
    {{"skill": "Docker", "level": "Intermediate", "category": "cloud_devops"}}
  ]
}}

Candidate Resume Text:
\"\"\"
{resume_text}
\"\"\"
"""

SKILL_GAP_PROMPT = """
Target Role: {target_role}

Candidate Skills:
{candidate_skills}

Analyze the skill gaps between the candidate's profile and the target role requirements.
Categorize skills into Available, Missing, and Partial.

Return ONLY valid JSON matching this schema:
{{
  "match_percentage": 78,
  "target_role": "{target_role}",
  "available": [
    {{"skill": "Java", "proficiency": "Advanced", "category": "backend"}}
  ],
  "missing": [
    {{
      "skill": "Docker",
      "importance": "High",
      "category": "cloud_devops",
      "reason": "Required for microservices containerization and CI/CD workflows",
      "prerequisites": ["Linux CLI"],
      "difficulty": "Intermediate"
    }}
  ],
  "partial": [
    {{"skill": "Microservices", "category": "backend", "gap_notes": "Understands basic concepts but lacks production deployment evidence"}}
  ],
  "recommendations": ["Recommendation 1", "Recommendation 2"]
}}
"""

PROJECT_GENERATOR_PROMPT = """
Candidate Target Role: {target_role}
Candidate Missing Skills: {missing_skills}

Generate a comprehensive portfolio project blueprint designed to help the candidate master missing skills.
Return ONLY valid JSON.
"""

ROADMAP_GENERATOR_PROMPT = """
Target Role: {target_role}
Candidate Current Skills: {current_skills}
Candidate Missing Skills: {missing_skills}

Generate a 6-step personalized, milestone-based career learning roadmap to master this role.
For each step, recommend specific top online platforms (e.g. Coursera, Udemy, YouTube, freeCodeCamp, edX, Official Documentation, LeetCode, GitHub Repositories).

Return ONLY valid JSON matching this schema:
{{
  "target_role": "{target_role}",
  "total_estimated_weeks": "12-16 Weeks",
  "steps": [
    {{
      "id": 1,
      "skill": "Java Core & Object-Oriented Programming",
      "category": "Programming",
      "difficulty": "Beginner",
      "estimated_time": "2 Weeks",
      "priority": "High",
      "status": "Not Started",
      "description": "Master core Java syntax, OOP design principles, and exception handling.",
      "prerequisites": ["Basic Logic"],
      "online_platform_recommendations": [
        {{
          "platform": "Coursera",
          "course_name": "Java Programming and Software Engineering Fundamentals (Duke University)",
          "type": "Interactive Course"
        }},
        {{
          "platform": "freeCodeCamp / YouTube",
          "course_name": "Java Tutorial for Beginners (Full Course)",
          "type": "Video Tutorial"
        }},
        {{
          "platform": "Official Docs",
          "course_name": "Oracle Java SE Documentation & Tutorials",
          "type": "Documentation"
        }}
      ]
    }}
  ]
}}
"""

INTERVIEW_GENERATOR_PROMPT = """
Candidate Resume Summary:
{resume_summary}
 
Extracted Skills:
{skills}
 
Target Role: {target_role}
 
Generate between 15 and 20 interview questions tailored specifically to this candidate's resume and target role.
Focus on the actual skills present in the resume, and prioritize technical, architecture, and behavioral questions that a recruiter or hiring manager would realistically ask.
Do not repeat similar questions. Make them progressive from fundamentals to deeper system design and problem-solving.
Return ONLY valid JSON matching this schema:
{{
  "questions": [
    {{
      "id": 1,
      "category": "Technical",
      "question": "How did you optimize database queries in your Spring Boot project?",
      "sample_answer": "Used JPA indexing, pagination, and lazy loading to eliminate N+1 queries.",
      "difficulty": "Intermediate"
    }}
  ]
}}
"""

TOPIC_ASSESSMENT_PROMPT = """
Candidate Resume Summary:
{resume_summary}

Extracted Skills:
{skills}

Target Role: {target_role}

Generate {question_count} multiple-choice assessment questions based strictly on the candidate's resume topics and target role.
Each question should test a technical concept directly tied to the resume's actual skills or role requirements.
Only return valid JSON.

Schema:
{{
  "questions": [
    {{
      "id": 1,
      "category": "Java",
      "question": "Which JVM concept is most relevant when optimizing memory usage in a Java backend system?",
      "options": ["Garbage Collection", "CSS selectors", "HTTP redirect rules", "SQL joins"],
      "correct_option": 0,
      "explanation": "Garbage Collection is a core Java memory-management concept for backend systems.",
      "difficulty": "Intermediate"
    }}
  ]
}}
"""

MOCK_INTERVIEW_EVALUATION_PROMPT = """
Interview Question: {question}
Candidate Answer: {answer}
 
Evaluate the candidate's answer for technical correctness, clarity, completeness, and confidence.
 
Return ONLY valid JSON matching this schema:
{{
  "score": 85,
  "technical_accuracy": "Strong",
  "completeness": "Good",
  "strengths": ["Clear explanation of core concepts"],
  "areas_for_improvement": ["Could mention specific metrics or benchmarks"],
  "improved_model_answer": "Model answer demonstrating ideal structure"
}}
"""


# ==========================================
# 2. Astra AI Career Assistant Modular Templates
# ==========================================

ASTRA_CHATBOT_SYSTEM_PROMPT = _load_template(
    "system_prompt.txt",
    """You are Astra, an expert AI Career Assistant and Mentor.

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
"""
)

ASTRA_RESUME_CONTEXT_TEMPLATE = _load_template(
    "resume_context.txt",
    """Candidate Profile Context:
Name: {name}
Target Role: {target_role}
ATS Score: {ats_score}/100
Current Skills: {skills}
Missing Skills: {missing_skills}
Matching Skills: {matching_skills}
Education: {education}
Experience: {experience}
Projects: {projects}
"""
)

ASTRA_CAREER_PROMPT_TEMPLATE = _load_template(
    "career_prompt.txt",
    """Target Role: {target_role}
Candidate Skills: {skills}
Skill Gaps: {missing_skills}

Provide clear, structured, and highly actionable career guidance tailored strictly to this candidate's background and target role.
"""
)

ASTRA_SKILL_GAP_PROMPT_TEMPLATE = _load_template(
    "skill_gap_prompt.txt",
    """Target Role: {target_role}
Candidate Current Skills: {skills}
Identified Missing Skills: {missing_skills}

Analyze the skill gaps. Prioritize which skills to learn first, explain why each skill is crucial for this role, and outline prerequisites.
"""
)

ASTRA_ATS_PROMPT_TEMPLATE = _load_template(
    "ats_prompt.txt",
    """Candidate ATS Score: {ats_score}/100
Matching Skills: {matching_skills}
Missing Keywords / Skills: {missing_skills}
Summary: {summary}

Explain why the candidate received this ATS score. Identify exact keywords missing from their resume, formatting risks, and concrete steps to increase their score.
"""
)

ASTRA_INTERVIEW_PROMPT_TEMPLATE = _load_template(
    "interview_prompt.txt",
    """Target Role: {target_role}
Candidate Skills: {skills}
Candidate Projects: {projects}

You are conducting a Mock Technical Interview.
Ask a clear, relevant technical or architectural question tailored to the candidate's background and target role.
When evaluating an answer, provide:
1. Technical Accuracy (score out of 10)
2. Completeness (score out of 10)
3. Clarity (score out of 10)
4. Specific actionable feedback and an improved model answer.
"""
)

ASTRA_CHATBOT_PROMPT_TEMPLATE = _load_template(
    "chatbot_prompt.txt",
    """User Message: {user_message}

Relevant Candidate Context:
{candidate_context}

Relevant Knowledge Context:
{rag_context}

Conversation History:
{history}

Answer as Astra, an encouraging, professional, and precise AI Career Assistant.
"""
)

def get_prompt_template(name: str) -> str:
    """Retrieve prompt template by name."""
    filename = f"{name}.txt" if not name.endswith(".txt") else name
    return _load_template(filename, "")
