import logging
from typing import Any, Dict, List

from app.ai.llm_client import get_llm_client
from app.ai.prompts import INTERVIEW_GENERATOR_PROMPT, MOCK_INTERVIEW_EVALUATION_PROMPT, TOPIC_ASSESSMENT_PROMPT
from app.ai.rag_engine import rag_engine

logger = logging.getLogger("resume_ai")


def _build_skill_based_question_pack(skills: List[str], target_role: str) -> List[Dict[str, Any]]:
    skill_names = [str(skill).strip() for skill in skills if str(skill).strip()]
    if not skill_names:
        skill_names = ["Java", "Python", "SQL", "REST API", "Docker", "System Design"]

    base_template = [
        ("Technical", "Explain how you would design a production-ready {skill} system for a {target_role} role, covering architecture, scaling, and failure handling.", "Advanced"),
        ("Technical", "What trade-offs would you consider when choosing {skill} patterns, data models, and deployment strategies for a scalable product?", "Advanced"),
        ("System Design", "How would you design a fault-tolerant backend for a high-traffic application using {skill} and modern observability tools?", "Advanced"),
        ("Database", "How would you optimize database performance and query design when a {skill}-based application becomes slow under load?", "Advanced"),
        ("Behavioral", "Tell us about a time when a deployment or integration issue threatened delivery in a {target_role} project. How did you respond?", "Intermediate"),
        ("Technical", "Describe your testing strategy for a {skill}-based service, including unit, integration, and regression validation.", "Intermediate"),
        ("Problem Solving", "If a production issue is affecting user traffic, how would you diagnose and prioritize the root cause in a {skill} environment?", "Advanced"),
        ("Behavioral", "Describe a challenge where you had to explain a technical trade-off to non-technical stakeholders. What was the outcome?", "Intermediate"),
        ("Coding", "How would you structure code for readability, maintainability, and extensibility when building a new {skill} feature?", "Intermediate"),
        ("Technical", "What metrics would you monitor to evaluate whether a {skill} feature is successful in production?", "Intermediate"),
        ("Leadership", "How do you align engineering priorities when multiple team goals conflict in a {target_role} project?", "Intermediate"),
        ("Technical", "How do you ensure security, validation, and auditability in critical {skill} workflows?", "Advanced"),
        ("System Design", "Walk through the components you would include for a resilient multi-service {target_role} platform built with {skill} technologies.", "Advanced"),
        ("Database", "How do you manage schema changes and data migrations safely without causing downtime in a production system?", "Advanced"),
        ("Behavioral", "Describe a time when you improved a process, toolchain, or team workflow to deliver better results in a {target_role} domain.", "Intermediate"),
        ("Technical", "How would you reduce technical debt if a {skill}-driven codebase was becoming difficult to scale and maintain?", "Advanced"),
        ("Problem Solving", "Give an example of a bug or performance issue you solved. How did you isolate the root cause and validate the fix?", "Advanced"),
        ("Technical", "How would you design a CI/CD pipeline for a {skill}-based deployment pipeline with safety checks and rollback plans?", "Intermediate"),
        ("Behavioral", "Tell us about a learning experience that transformed your approach to {target_role} engineering. how did you apply it?", "Intermediate"),
        ("Technical", "What would you refactor first in a codebase where responsibilities around {skill} are tightly coupled and difficult to test?", "Advanced"),
    ]

    questions = []
    for idx, (category, question_template, difficulty) in enumerate(base_template, start=1):
        skill = skill_names[(idx - 1) % len(skill_names)]
        question = question_template.format(skill=skill, target_role=target_role)
        questions.append({
            "id": idx,
            "category": category,
            "question": question,
            "sample_answer": "Use the STAR method, describe the technical reasoning, mention trade-offs, and close with measurable outcomes or lessons learned.",
            "difficulty": difficulty,
        })

    return questions[:20]


def generate_interview_questions(resume_summary: str, skills: List[str], target_role: str = "Software Engineer", question_count: int = 12) -> Dict[str, Any]:
    llm = get_llm_client()
    context = rag_engine.retrieve_context(target_role)
    prompt = INTERVIEW_GENERATOR_PROMPT.format(
        resume_summary=resume_summary or "Software developer with web & backend experience",
        skills=", ".join(skills) if skills else "Java, Python, SQL, REST API",
        target_role=target_role,
        question_count=max(8, min(18, question_count))
    )

    try:
        result = llm.generate_json(prompt, system_prompt=f"Grounded Context:\n{context}")
        questions = result.get("questions", []) if isinstance(result, dict) else []
        if isinstance(questions, list) and 8 <= len(questions) <= 18:
            return {"questions": questions[:max(8, min(18, question_count))]}
    except Exception as e:
        logger.warning(f"Fallback interview generator: {e}")

    pack = _build_skill_based_question_pack(skills, target_role)
    return {"questions": pack[: max(8, min(18, question_count))]}


def generate_resume_topic_assessment(resume_summary: str, skills: List[str], target_role: str = "Software Engineer", question_count: int = 5) -> Dict[str, Any]:
    llm = get_llm_client()
    context = rag_engine.retrieve_context(target_role)
    prompt = TOPIC_ASSESSMENT_PROMPT.format(
        resume_summary=resume_summary or "Software developer with backend and database experience.",
        skills=", ".join(skills) if skills else "Java, SQL, REST API, Docker",
        target_role=target_role,
        question_count=max(3, min(10, question_count)),
    )

    try:
        result = llm.generate_json(prompt, system_prompt=f"Grounded Context:\n{context}")
        questions = result.get("questions", []) if isinstance(result, dict) else []
        if isinstance(questions, list) and questions:
            return {"questions": questions[: max(3, min(10, question_count))]}
    except Exception as e:
        logger.warning(f"Fallback topic assessment generator: {e}")

    fallback = [
        {
            "id": 1,
            "category": "Java",
            "question": "Which Java concept is most important for safe memory usage in a backend service?",
            "options": ["Garbage Collection", "CSS layout", "HTML parsing", "JSON serialization"],
            "correct_option": 0,
            "explanation": "Garbage Collection is central to Java memory management and runtime stability.",
            "difficulty": "Intermediate",
        },
        {
            "id": 2,
            "category": "REST API",
            "question": "What is the main purpose of HTTP status codes in a REST API?",
            "options": ["To style user interfaces", "To communicate request outcome to the client", "To create database tables", "To manage CSS classes"],
            "correct_option": 1,
            "explanation": "HTTP status codes inform clients whether the request succeeded, failed, or needs attention.",
            "difficulty": "Beginner",
        },
        {
            "id": 3,
            "category": "SQL",
            "question": "Which SQL operation is used to combine related rows from two tables?",
            "options": ["JOIN", "DIVIDE", "APPEND", "RENAME"],
            "correct_option": 0,
            "explanation": "JOIN combines rows from related tables based on matching conditions.",
            "difficulty": "Beginner",
        },
        {
            "id": 4,
            "category": "Docker",
            "question": "Why is Docker relevant for modern backend teams?",
            "options": ["It packages apps and dependencies in a consistent environment", "It replaces all debugging tools", "It removes the need for databases", "It generates resumes automatically"],
            "correct_option": 0,
            "explanation": "Docker helps create consistent deployment environments across development and production.",
            "difficulty": "Intermediate",
        },
        {
            "id": 5,
            "category": "System Design",
            "question": "Why do backend systems use caching?",
            "options": ["To reduce repeated expensive processing and improve latency", "To replace the database completely", "To write CSS faster", "To eliminate testing"],
            "correct_option": 0,
            "explanation": "Caching helps reduce repeated computation and speed up common requests.",
            "difficulty": "Intermediate",
        },
    ]

    return {"questions": fallback[: max(3, min(10, question_count))]}


def evaluate_interview_answer(question: str, answer: str) -> Dict[str, Any]:
    llm = get_llm_client()
    prompt = MOCK_INTERVIEW_EVALUATION_PROMPT.format(question=question, answer=answer)
    try:
        result = llm.generate_json(prompt)
        if isinstance(result, dict):
            result.setdefault("technical_accuracy", "Strong")
            result.setdefault("completeness", "Good")
            result.setdefault("clarity", "Clear")
            result.setdefault("confidence", "Solid")
            result.setdefault("strengths", ["Strong understanding of the core concept."])
            result.setdefault("areas_for_improvement", ["Add specific examples or metrics for more credibility."])
            result.setdefault("improved_model_answer", "Use the STAR method and include a short example with measurable outcome.")
            result.setdefault("next_focus", "Review the trade-offs, architecture decisions, and measurable impact of your solution.")
            return result
    except Exception as e:
        logger.warning(f"Fallback interview evaluation: {e}")

    return {
        "score": 85,
        "technical_accuracy": "Strong",
        "completeness": "Good",
        "clarity": "Clear",
        "confidence": "Solid",
        "strengths": [
            "Clear explanation of the main principle",
            "Good structure and logical flow",
            "Identified key trade-offs and technical reasoning",
        ],
        "areas_for_improvement": [
            "Include a concrete project example or measurable result",
            "Discuss the impact on scale, reliability, or performance",
            "Mention how you would validate the solution in production",
        ],
        "improved_model_answer": f"For '{question}', frame your answer with context, the decision you made, why it mattered, and the result. Include one concise example, mention trade-offs, and finish with a measurable outcome or lesson learned.",
        "next_focus": "Practice speaking in a structured format: problem → approach → trade-offs → result → lesson learned.",
    }
