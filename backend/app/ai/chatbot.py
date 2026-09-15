import json
import logging
from typing import Any, Dict, Iterator, List, Optional
from app.ai.gemini_client import get_gemini_client
from app.ai.prompts import ASTRA_CHATBOT_SYSTEM_PROMPT
from app.ai.rag_engine import rag_engine
from app.ai.context_manager import ContextManager

logger = logging.getLogger("resume_ai")


def normalize_resume_context(raw_resume: Optional[Dict[str, Any]], fallback_role: str = "Software Engineer") -> Dict[str, Any]:
    """Normalize resume data from multiple parser shapes into a consistent Astra context object."""
    data = raw_resume or {}
    sections = data.get("sections") if isinstance(data.get("sections"), dict) else {}
    personal_info = data.get("personal_info") if isinstance(data.get("personal_info"), dict) else {}

    target_role = (
        data.get("target_role")
        or data.get("job_target_role")
        or sections.get("target_role")
        or fallback_role
    )

    skills = data.get("all_skills") or data.get("skills") or []
    missing_skills = data.get("missing_skills") or data.get("skill_gaps") or []
    matching_skills = data.get("matching_skills") or []
    ats_score = data.get("ats_score")
    if ats_score is None:
        ats_score = data.get("ats") or data.get("score") or 0

    normalized = {
        "name": data.get("name") or personal_info.get("name") or "Candidate",
        "target_role": target_role,
        "summary": data.get("summary") or sections.get("summary") or personal_info.get("summary") or "",
        "skills": [str(skill) for skill in skills],
        "missing_skills": [str(skill) for skill in missing_skills],
        "matching_skills": [str(skill) for skill in matching_skills],
        "ats_score": float(ats_score) if isinstance(ats_score, (int, float)) else 0,
        "experience": data.get("experience") or sections.get("experience") or [],
        "projects": data.get("projects") or sections.get("projects") or [],
        "education": data.get("education") or sections.get("education") or [],
    }

    if not normalized["skills"] and isinstance(data.get("skills_by_category"), dict):
        for item in data["skills_by_category"].values():
            if isinstance(item, list):
                normalized["skills"].extend(str(skill) for skill in item)

    if not normalized["missing_skills"] and isinstance(data.get("missing_skills_detail"), list):
        normalized["missing_skills"] = [str(skill) for skill in data["missing_skills_detail"]]

    return normalized


def _build_full_prompt(
    user_message: str,
    context_pkg: Dict[str, Any],
    rag_context: str
) -> str:
    compact_ctx = context_pkg.get("compact_context", "")
    history = context_pkg.get("history", "")
    intent = context_pkg.get("intent", "general_career")

    return f"""Candidate Resume Context:
{compact_ctx}

Retrieved Technical & Career Knowledge Base:
{rag_context}

Recent Conversation History:
{history}

Detected Query Intent: {intent}

Candidate Message:
"{user_message}"

Instruction for Astra:
Respond in a warm, professional, encouraging, and highly specific tone as Astra, the AI Career Assistant.
- If the user asks about their resume, ATS score, or skills, cite their actual context above.
- If something is missing from their profile, state honestly that it was not detected in their uploaded resume.
- Prioritize actionable steps with clear technical rationale.
- Use markdown formatting with bullet points and bold highlights for readability.
"""


def _generate_fallback_response(
    user_message: str,
    context_pkg: Dict[str, Any],
    rag_context: str
) -> str:
    """High-intelligence personalized fallback generator when Gemini API key is not configured."""
    candidate = context_pkg.get("candidate_data", {})
    intent = context_pkg.get("intent", "general_career")

    name = candidate.get("name", "Candidate")
    target_role = candidate.get("target_role", "Software Engineer")
    skills = candidate.get("skills", ["Java", "SQL", "Git"])
    missing_skills = candidate.get("missing_skills", ["Spring Boot", "Docker", "REST API", "AWS"])
    ats_score = candidate.get("ats_score", 78)

    skills_str = ", ".join(str(s) for s in skills[:6]) or "fundamental software skills"
    missing_str = ", ".join(str(s) for s in missing_skills[:4]) or "modern cloud and backend frameworks"
    first_missing = missing_skills[0] if missing_skills else "Spring Boot"

    if intent == "ats":
        return f"""### 📊 ATS Score Analysis for {name}

Your current resume achieved an **ATS score of {ats_score}/100** for the **{target_role}** benchmark.

**Why this score was awarded:**
1. **Skill Coverage**: You have validated strength in **{skills_str}**.
2. **Missing Keywords**: Recruiter parsing engines look for high-frequency competencies such as **{missing_str}**, which were either absent or insufficiently highlighted in your experience bullets.
3. **Action Verb Impact**: Ensure every project and job bullet begins with a strong quantifiable action verb (e.g., *"Architected RESTful microservices reducing latency by 35%"*).

**Recommended Next Step:**
Add targeted keywords from **{missing_str}** into your project descriptions, and ensure your resume uses a clean single-column ATS-friendly layout."""

    elif intent in ("skill_gap", "learning"):
        return f"""### 🎯 Personalized Learning Recommendations

Based on your resume, you have solid foundations in **{skills_str}**. Your target role is **{target_role}**.

Your highest-priority missing skill is **{first_missing}**.

**Recommended Step-by-Step Path:**
1. **{first_missing} Fundamentals**: Learn core architecture, dependency injection, and component configuration.
2. **RESTful APIs**: Build end-to-end CRUD services with validation and structured exception handling.
3. **Database Integration**: Connect JPA / Hibernate with MySQL or PostgreSQL for persistence.
4. **Containerization with Docker**: Containerize your application with a multi-stage Dockerfile and test locally.

*Mastering {first_missing} will bridge your primary skill gap and boost your role match percentage significantly!*"""

    elif intent == "interview":
        return f"""### 🎤 Mock Interview Practice for {target_role}

Here is a targeted technical interview question based on your profile:

> **Question:**
> *"In your backend projects using {skills_str.split(',')[0] if skills else 'Java'}, how do you design RESTful endpoints for high scalability, and how do you prevent common database query bottlenecks such as the N+1 problem?"*

**Preparation Tip:**
Structure your response using the **STAR Method** (Situation, Task, Action, Result) or discuss architectural trade-offs between lazy loading vs `JOIN FETCH`.

Would you like to provide your answer so I can evaluate your technical accuracy and clarity?"""

    elif intent == "technical_question":
        return f"""### 💡 Technical Explanation

Here is a clear breakdown relevant to modern **{target_role}** ecosystems:

A **REST API (Representational State Transfer)** is an architectural style for network communications using standard HTTP protocols (`GET`, `POST`, `PUT`, `DELETE`).

**How It Connects to Your Stack:**
- **Language**: {skills_str.split(',')[0] if skills else 'Java / Python'}
- **Framework**: {first_missing} creates REST controllers to serve JSON payloads to web/mobile clients.
- **Database**: The API queries your database via an ORM and returns structured data.

*Pro-Tip: Ensure your REST APIs return appropriate HTTP status codes (`200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`).*"""

    elif intent == "job_role":
        return f"""### 💼 Career Suitability for {target_role}

Based on your extracted skills (**{skills_str}**), you have strong core competence for entry-to-mid level software engineering positions.

To be fully competitive for senior **{target_role}** openings:
- Bridge your identified skill gaps: **{missing_str}**.
- Highlight production metrics in your past projects.
- Include a deployed live demo link or GitHub repository showcasing containerized microservices."""

    else:
        return f"""Hello! As **Astra**, your AI Career Assistant, I have analyzed your resume profile for the **{target_role}** role.

- **ATS Compatibility**: {ats_score}/100
- **Strong Skills**: {skills_str}
- **High-Priority Gaps**: {missing_str}

Feel free to ask me anything about:
- Improving your ATS score and resume bullets
- Step-by-step learning roadmap for **{first_missing}**
- Practicing mock interview questions
- Technical concept explanations"""


def chat_with_astra(
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    candidate_context: Optional[Dict[str, Any]] = None
) -> str:
    """Core conversational entry point for Astra AI Career Assistant."""
    manager = ContextManager(candidate_context or {})
    context_pkg = manager.build_context_package(user_message, conversation_history)
    rag_context = rag_engine.retrieve_context(user_message, top_k=2)

    gemini = get_gemini_client()
    if gemini.available:
        try:
            full_prompt = _build_full_prompt(user_message, context_pkg, rag_context)
            return gemini.generate_text(full_prompt, system_prompt=ASTRA_CHATBOT_SYSTEM_PROMPT)
        except Exception as e:
            logger.warning(f"Gemini API invocation error: {e}. Falling back to structured response engine.")

    return _generate_fallback_response(user_message, context_pkg, rag_context)


def stream_chat_with_astra(
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    candidate_context: Optional[Dict[str, Any]] = None
) -> Iterator[str]:
    """Streaming entry point yielding tokens/chunks for Astra."""
    manager = ContextManager(candidate_context or {})
    context_pkg = manager.build_context_package(user_message, conversation_history)
    rag_context = rag_engine.retrieve_context(user_message, top_k=2)

    gemini = get_gemini_client()
    if gemini.available:
        try:
            full_prompt = _build_full_prompt(user_message, context_pkg, rag_context)
            for chunk in gemini.stream_text(full_prompt, system_prompt=ASTRA_CHATBOT_SYSTEM_PROMPT):
                yield chunk
            return
        except Exception as e:
            logger.warning(f"Gemini stream error: {e}. Using fallback stream.")

    fallback_text = _generate_fallback_response(user_message, context_pkg, rag_context)
    # Simulate gentle chunking for smooth UI streaming experience
    words = fallback_text.split(" ")
    chunk_size = 4
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i : i + chunk_size]) + " "


def evaluate_interview_answer(
    question: str,
    candidate_answer: str,
    target_role: str = "Software Engineer"
) -> Dict[str, Any]:
    """Evaluate candidate's interview answer with scoring and structured feedback."""
    prompt = f"""Target Role: {target_role}
Interview Question: {question}
Candidate Answer: {candidate_answer}

Evaluate this response thoroughly on:
1. Technical Accuracy (score 1-10)
2. Completeness (score 1-10)
3. Clarity (score 1-10)
4. Strengths
5. Areas for improvement
6. Improved model answer

Return ONLY valid JSON matching this schema:
{{
  "score": 85,
  "technical_accuracy": "8/10",
  "completeness": "7/10",
  "clarity": "8/10",
  "strengths": ["Clear explanation of core concepts"],
  "areas_for_improvement": ["Mention specific performance metrics and benchmarks"],
  "feedback": "Your answer is accurate and well structured. To make it senior-level, include trade-offs.",
  "improved_model_answer": "A structured model answer..."
}}"""

    gemini = get_gemini_client()
    if gemini.available:
        try:
            return gemini.generate_json(prompt, system_prompt="You are an expert technical hiring manager.")
        except Exception as e:
            logger.warning(f"Interview evaluation Gemini error: {e}")

    # Fallback Evaluation
    word_count = len(candidate_answer.split())
    base_score = min(92, max(65, 60 + word_count * 2))
    return {
        "score": base_score,
        "technical_accuracy": "8/10",
        "completeness": "8/10",
        "clarity": "8/10",
        "strengths": [
            "Addressed the core question directly",
            "Demonstrated logical flow and structured technical thinking"
        ],
        "areas_for_improvement": [
            "Include concrete examples or quantifiable production metrics",
            "Discuss edge cases and architectural trade-offs"
        ],
        "feedback": "Good response! You clearly understand the foundational architecture. Adding specific real-world examples and metrics will take your score above 90%.",
        "improved_model_answer": f"In a production {target_role} system, I approach this by separating concerns across architectural layers, applying connection pooling, and adding monitoring for latency and error rates."
    }
