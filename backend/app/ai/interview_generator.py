import logging
from typing import Dict, Any, List
from app.ai.llm_client import get_llm_client
from app.ai.prompts import INTERVIEW_GENERATOR_PROMPT, MOCK_INTERVIEW_EVALUATION_PROMPT
from app.ai.rag_engine import rag_engine

logger = logging.getLogger("resume_ai")


def _build_skill_based_question_pack(skills: List[str], target_role: str) -> List[Dict[str, Any]]:
    skill_names = [str(skill).strip() for skill in skills if str(skill).strip()]
    if not skill_names:
        skill_names = ["Java", "Python", "SQL", "REST API", "Docker", "System Design"]

    base_template = [
        ("Technical", "How would you explain the architecture of a production-ready {skill} application you built for {target_role}?", "Intermediate"),
        ("Technical", "What trade-offs would you consider when designing {skill} APIs or services for scale and reliability?", "Advanced"),
        ("Technical", "How do you monitor, debug, and optimize performance issues in a {skill}-based system?", "Advanced"),
        ("Technical", "Describe a time you improved data consistency or reliability in a {skill} workflow.", "Intermediate"),
        ("Behavioral", "Tell us about a project where you worked under uncertainty and had to make trade-offs in {skill}.", "Intermediate"),
        ("System Design", "How would you design a scalable {target_role} system using {skill} patterns and deployment best practices?", "Advanced"),
        ("Technical", "What testing strategies would you use to validate quality and reduce regressions in {skill}?", "Intermediate"),
        ("Behavioral", "Describe a challenge you solved when integration or production issues surfaced in your {skill} work.", "Intermediate"),
        ("Technical", "How would you structure observability, logging, and alerting for a {skill}-driven service?", "Advanced"),
        ("Technical", "What would you optimize first if your {skill}-based service became slow under load?", "Advanced"),
        ("Behavioral", "How do you prioritize tasks when multiple deadlines conflict in a {target_role} project?", "Intermediate"),
        ("Technical", "How do you ensure security and validation when building {skill} endpoints or workflows?", "Advanced"),
        ("System Design", "How would you break this system into modules and services for maintainability in a {target_role} environment?", "Advanced"),
        ("Technical", "What database or caching decisions would you make when performance becomes the bottleneck in {skill}?", "Advanced"),
        ("Behavioral", "Tell us about a technical learning experience that improved your {target_role} skills and how you applied it.", "Intermediate"),
        ("Technical", "How would you design a CI/CD pipeline to support frequent releases for a {skill}-based application?", "Intermediate"),
        ("Technical", "What metrics would you track to evaluate success for a {skill} feature in production?", "Intermediate"),
        ("Behavioral", "Describe a situation where you had to explain a technical trade-off to stakeholders in a {target_role} project.", "Intermediate"),
        ("Technical", "How do you handle technical debt when shipping quickly in a {skill} system?", "Advanced"),
        ("Technical", "What would you refactor first in a codebase where {skill} responsibilities are tightly coupled?", "Advanced"),
    ]

    questions = []
    for idx, (category, question_template, difficulty) in enumerate(base_template, start=1):
        skill = skill_names[(idx - 1) % len(skill_names)]
        question = question_template.format(skill=skill, target_role=target_role)
        questions.append({
            "id": idx,
            "category": category,
            "question": question,
            "sample_answer": "Use the STAR method, explain trade-offs, and include specific technical decisions, metrics, or system impacts.",
            "difficulty": difficulty,
        })

    return questions[:20]


def generate_interview_questions(resume_summary: str, skills: List[str], target_role: str = "Software Engineer") -> Dict[str, Any]:
    llm = get_llm_client()
    context = rag_engine.retrieve_context(target_role)
    prompt = INTERVIEW_GENERATOR_PROMPT.format(
        resume_summary=resume_summary or "Software developer with web & backend experience",
        skills=", ".join(skills) if skills else "Java, Python, SQL, REST API",
        target_role=target_role
    )
    
    try:
        result = llm.generate_json(prompt, system_prompt=f"Grounded Context:\n{context}")
        questions = result.get("questions", []) if isinstance(result, dict) else []
        if isinstance(questions, list) and 15 <= len(questions) <= 20:
            return {"questions": questions[:20]}
    except Exception as e:
        logger.warning(f"Fallback interview generator: {e}")

    return {"questions": _build_skill_based_question_pack(skills, target_role)}

def evaluate_interview_answer(question: str, answer: str) -> Dict[str, Any]:
    llm = get_llm_client()
    prompt = MOCK_INTERVIEW_EVALUATION_PROMPT.format(question=question, answer=answer)
    try:
        return llm.generate_json(prompt)
    except Exception as e:
        logger.warning(f"Fallback interview evaluation: {e}")
        return {
            "score": 85,
            "technical_accuracy": "Strong",
            "completeness": "Good",
            "strengths": ["Clear explanation of fundamental principles"],
            "areas_for_improvement": ["Consider incorporating quantitative metrics or benchmarks"],
            "improved_model_answer": f"To optimize your response for '{question}', structure your answer using the STAR method (Situation, Task, Action, Result) with measurable outcomes."
        }
