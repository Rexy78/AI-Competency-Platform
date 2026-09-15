from app.ai.chatbot import normalize_resume_context


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
