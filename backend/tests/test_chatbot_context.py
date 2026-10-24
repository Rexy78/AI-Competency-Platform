from app.ai.chatbot import _build_full_prompt, _generate_fallback_response, normalize_resume_context
from app.ai.context_manager import ContextManager


def test_normalize_resume_context_uses_resume_data():
    resume_data = {
        "target_role": "Java Backend Developer",
        "summary": "Backend engineer with Java and Spring Boot experience.",
        "all_skills": ["Java", "Spring Boot", "REST API", "Docker", "SQL"],
        "missing_skills": ["Kubernetes", "AWS"],
        "ats_score": 89,
    }

    ctx = normalize_resume_context(resume_data, "Software Engineer")

    assert ctx["target_role"] == "Java Backend Developer"
    assert "Spring Boot" in ctx["skills"]
    assert "Kubernetes" in ctx["missing_skills"]
    assert ctx["ats_score"] == 89


def test_normalize_resume_context_falls_back_safely():
    ctx = normalize_resume_context({}, "Python Developer")

    assert ctx["target_role"] == "Python Developer"
    assert isinstance(ctx["skills"], list)
    assert isinstance(ctx["missing_skills"], list)


def test_fallback_answers_are_specific_to_the_question():
    context = {
        "intent": "ats",
        "candidate_data": {
            "name": "Candidate",
            "target_role": "Python Developer",
            "skills": [],
            "missing_skills": [],
            "ats_score": 0,
        },
        "history": "No previous conversation history.",
    }

    response = _generate_fallback_response("Why is my ATS score low?", context, "")

    assert "don't have an analyzed ATS score" in response
    assert "Spring Boot" not in response


def test_skill_gap_fallback_reports_analyzed_role_requirements():
    context = {
        "intent": "skill_gap",
        "candidate_data": {
            "target_role": "Java Backend Developer",
            "skills": ["Java", "SQL", "Git"],
            "skill_gap_status": "analyzed",
            "skill_match_percentage": 33,
            "gap_matrix": [
                {"skill": "Java", "status": "Available", "priority": "—"},
                {"skill": "Spring Boot", "status": "Missing", "priority": "High"},
            ],
            "recommendations": [
                {"skill": "Spring Boot", "next_steps": ["REST APIs", "Spring Data JPA"]},
            ],
        },
    }

    response = _generate_fallback_response("Identify my skill gaps", context, "")

    assert "Java Backend Developer" in response
    assert "33%" in response
    assert "Spring Boot (High priority)" in response
    assert "REST APIs" in response


def test_skill_gap_fallback_does_not_invent_gaps_without_resume():
    context = {
        "intent": "skill_gap",
        "candidate_data": {
            "target_role": "Python Developer",
            "skills": [],
            "missing_skills": [],
            "skill_gap_status": "no_resume",
        },
    }

    response = _generate_fallback_response("Identify my skill gaps", context, "")

    assert "Upload your resume first" in response
    assert "Spring Boot" not in response


def test_chat_prompt_uses_history_and_avoids_repeating_answers():
    context = {
        "compact_context": "Target Role: Python Developer",
        "history": "Candidate: How do I improve?\nAstra: Start by tailoring your resume.",
        "intent": "general_career",
    }

    prompt = _build_full_prompt("What should I do next?", context, "")

    assert "Start by tailoring your resume." in prompt
    assert "do not repeat an earlier answer verbatim" in prompt


def test_context_manager_detects_skill_priority_questions():
    context = ContextManager({"target_role": "Python Developer"}).build_context_package(
        "Which skills should I focus on for my target role?"
    )

    assert context["intent"] == "skill_gap"
