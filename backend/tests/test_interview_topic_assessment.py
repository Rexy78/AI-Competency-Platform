import pytest
from fastapi import HTTPException

from app.routes import interview


def test_topic_assessment_generates_questions_from_resume_context(monkeypatch):
    calls = {}

    def load_profile(user, db):
        return (
            {"experience": ["Backend developer"], "projects": ["Inventory API"]},
            ["Java", "SQL"],
            "Software Engineer",
            [],
        )

    def generate(summary, skills, role, question_count):
        calls.update(summary=summary, skills=skills, role=role, question_count=question_count)
        return {
            "questions": [
                {
                    "category": "Java",
                    "question": "Which feature manages unused heap objects?",
                    "options": ["Garbage collection", "CSS grid", "HTML parsing", "DNS"],
                    "correct_option": "A",
                    "explanation": "The JVM garbage collector reclaims unreachable objects.",
                    "difficulty": "Intermediate",
                },
                {"question": "Invalid item", "options": ["A", "B"], "correct_option": 4},
            ]
        }

    monkeypatch.setattr(interview, "_load_resume_context", load_profile)
    monkeypatch.setattr(interview, "generate_resume_topic_assessment", generate)

    response = interview.get_topic_test(
        interview.LegacyQuestionGenRequest(target_role="Java Backend Developer", question_count=5),
        current_user=object(),
        db=object(),
    )

    assert calls["skills"] == ["Java", "SQL"]
    assert calls["role"] == "Java Backend Developer"
    assert calls["question_count"] == 5
    assert "Inventory API" in calls["summary"]
    assert response["questions"] == [{
        "id": 1,
        "category": "Java",
        "question": "Which feature manages unused heap objects?",
        "options": ["Garbage collection", "CSS grid", "HTML parsing", "DNS"],
        "correct_option": 0,
        "explanation": "The JVM garbage collector reclaims unreachable objects.",
        "difficulty": "Intermediate",
    }]


def test_topic_assessment_reports_when_generation_returns_no_valid_questions(monkeypatch):
    monkeypatch.setattr(interview, "_load_resume_context", lambda user, db: ({}, [], "Software Engineer", []))
    monkeypatch.setattr(interview, "generate_resume_topic_assessment", lambda *args: {"questions": []})

    with pytest.raises(HTTPException) as error:
        interview.get_topic_test(
            interview.LegacyQuestionGenRequest(),
            current_user=object(),
            db=object(),
        )

    assert error.value.status_code == 502
