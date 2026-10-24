import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    PracticeAnswer,
    PracticeAssessment,
    PracticeCodingProblem,
    PracticeCodingSubmission,
    PracticePerformance,
    PracticeRecommendation,
    User,
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/practice", tags=["Practice Platform"])

QUESTION_BANK = {
    "communication": [
        {
            "id": "comm-1",
            "question": "Choose the correct sentence.",
            "options": ["She don’t know the answer.", "She doesn't know the answer.", "She not know the answer.", "She didn't know the answer to."],
            "correct_answer": "B",
            "explanation": "The subject 'she' takes 'doesn't' in the present tense.",
            "difficulty": "Easy",
            "topic": "Grammar",
            "marks": 1,
            "negative_marks": 0.25,
        },
        {
            "id": "comm-2",
            "question": "Which word is closest in meaning to 'frugal'?",
            "options": ["Wasteful", "Economical", "Careless", "Generous"],
            "correct_answer": "B",
            "explanation": "Frugal means economical and avoiding waste.",
            "difficulty": "Medium",
            "topic": "Vocabulary",
            "marks": 1,
            "negative_marks": 0.25,
        },
        {
            "id": "comm-3",
            "question": "Which sentence is the most professional response to a client delay?",
            "options": ["The client is wrong.", "We are working on it and will share an update soon.", "It is not my problem.", "We do not know what to do."],
            "correct_answer": "B",
            "explanation": "Professional communication shows ownership, clarity, and reassurance.",
            "difficulty": "Medium",
            "topic": "Professional Communication",
            "marks": 1,
            "negative_marks": 0.25,
        },
    ],
    "aptitude": [
        {
            "id": "apt-1",
            "question": "If 20% of a number is 40, what is the number?",
            "options": ["100", "150", "200", "250"],
            "correct_answer": "C",
            "explanation": "20% of 200 is 40.",
            "difficulty": "Easy",
            "topic": "Percentages",
            "marks": 1,
            "negative_marks": 0.25,
        },
        {
            "id": "apt-2",
            "question": "A train covers 180 km in 3 hours. What is its speed?",
            "options": ["50 km/h", "55 km/h", "60 km/h", "65 km/h"],
            "correct_answer": "C",
            "explanation": "Speed = distance / time = 180 / 3 = 60 km/h.",
            "difficulty": "Easy",
            "topic": "Speed and Distance",
            "marks": 1,
            "negative_marks": 0.25,
        },
        {
            "id": "apt-3",
            "question": "The average of 5, 8, 11, 14, 17 is:",
            "options": ["10", "11", "12", "13"],
            "correct_answer": "B",
            "explanation": "Sum = 55; 55 / 5 = 11.",
            "difficulty": "Easy",
            "topic": "Average",
            "marks": 1,
            "negative_marks": 0.25,
        },
    ],
    "logical": [
        {
            "id": "log-1",
            "question": "Find the next number: 2, 6, 12, 20, 30, ?",
            "options": ["36", "38", "40", "42"],
            "correct_answer": "C",
            "explanation": "The pattern is n(n+1): 2, 6, 12, 20, 30, 42.",
            "difficulty": "Medium",
            "topic": "Number Series",
            "marks": 1,
            "negative_marks": 0.25,
        },
        {
            "id": "log-2",
            "question": "If A is the father of B and B is the father of C, what is A to C?",
            "options": ["Brother", "Grandfather", "Father", "Uncle"],
            "correct_answer": "B",
            "explanation": "A is the grandfather of C.",
            "difficulty": "Medium",
            "topic": "Blood Relations",
            "marks": 1,
            "negative_marks": 0.25,
        },
    ],
    "reasoning": [
        {
            "id": "rea-1",
            "question": "Which of the following is the odd one out?",
            "options": ["Triangle", "Square", "Circle", "Rectangle"],
            "correct_answer": "C",
            "explanation": "Circle has no sides, while the rest are polygons.",
            "difficulty": "Easy",
            "topic": "Classification",
            "marks": 1,
            "negative_marks": 0.25,
        },
        {
            "id": "rea-2",
            "question": "If in a code language, TRAIN = UQBJQ, then PLANE = ?",
            "options": ["QMBMF", "QMBNF", "QMBMF", "QMBQF"],
            "correct_answer": "A",
            "explanation": "Each letter is shifted by +1 in the alphabet.",
            "difficulty": "Medium",
            "topic": "Coding-Decoding",
            "marks": 1,
            "negative_marks": 0.25,
        },
    ],
    "technical": [
        {
            "id": "tech-1",
            "question": "Which Java collection maintains insertion order?",
            "options": ["HashSet", "TreeSet", "LinkedHashSet", "HashMap"],
            "correct_answer": "C",
            "explanation": "LinkedHashSet stores elements in insertion order.",
            "difficulty": "Medium",
            "topic": "Java Collections",
            "marks": 1,
            "negative_marks": 0.25,
        },
        {
            "id": "tech-2",
            "question": "Which SQL clause is used to filter rows after grouping?",
            "options": ["WHERE", "HAVING", "GROUP BY", "ORDER BY"],
            "correct_answer": "B",
            "explanation": "HAVING filters grouped data after aggregation.",
            "difficulty": "Medium",
            "topic": "SQL",
            "marks": 1,
            "negative_marks": 0.25,
        },
        {
            "id": "tech-3",
            "question": "What is the time complexity of binary search in a sorted array?",
            "options": ["O(n)", "O(log n)", "O(n log n)", "O(1)"],
            "correct_answer": "B",
            "explanation": "Binary search halves the search space each step, so the complexity is O(log n).",
            "difficulty": "Medium",
            "topic": "Data Structures",
            "marks": 1,
            "negative_marks": 0.25,
        },
    ],
}

CODING_PROBLEMS = [
    {
        "id": 1,
        "title": "Find Maximum in Array",
        "description": "Given an array of integers, find the maximum value in the array.",
        "input_format": "First line contains n, next line contains n integers.",
        "output_format": "Print the maximum element.",
        "constraints": "1 <= n <= 10^5, values within 32-bit integer range.",
        "difficulty": "Easy",
        "topic": "Arrays",
        "example_input": "5\n1 3 7 2 9",
        "example_output": "9",
        "template": "def max_in_array(arr):\n    pass\n",
        "supported_languages": ["Python", "Java", "C++", "C"],
        "public_test_cases": [{"input": "5\n1 3 7 2 9", "output": "9"}],
        "hidden_test_cases": [{"input": "4\n10 2 9 6", "output": "10"}],
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
    },
    {
        "id": 2,
        "title": "Reverse a String",
        "description": "Given a string, print the reversed version of the string.",
        "input_format": "Single string input.",
        "output_format": "Print the reversed string.",
        "constraints": "Length of string <= 10^5.",
        "difficulty": "Easy",
        "topic": "Strings",
        "example_input": "hello",
        "example_output": "olleh",
        "template": "def reverse_string(s):\n    pass\n",
        "supported_languages": ["Python", "Java", "C++", "C"],
        "public_test_cases": [{"input": "hello", "output": "olleh"}],
        "hidden_test_cases": [{"input": "resume", "output": "emuser"}],
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
    },
]


def _category_title(category: str) -> str:
    mapping = {
        "communication": "Communication",
        "aptitude": "Quantitative Aptitude",
        "logical": "Logical Ability",
        "reasoning": "Reasoning",
        "technical": "Technical MCQ",
    }
    return mapping.get(category, category.title())


def _pick_questions(category: str, limit: int = 10) -> List[Dict[str, Any]]:
    items = QUESTION_BANK.get(category, [])
    if not items:
        return []
    selected = []
    for i in range(min(limit, len(items))):
        question = dict(items[i % len(items)])
        selected.append(question)
    return selected


def _build_result(questions: List[Dict[str, Any]], responses: Dict[str, Any]) -> Dict[str, Any]:
    section_scores: Dict[str, float] = {}
    section_counts: Dict[str, int] = {}
    total = 0
    correct = 0
    attempted = 0
    incorrect = 0

    for question in questions:
        category = question.get("category") or "technical"
        answer = responses.get(question["id"])
        is_correct = bool(answer and answer.get("selected_option") == question["correct_answer"])
        if answer:
            attempted += 1
            if is_correct:
                correct += 1
                total += float(question.get("marks", 1))
            else:
                incorrect += 1
                total -= float(question.get("negative_marks", 0.25))
        section_scores.setdefault(category, 0)
        section_counts.setdefault(category, 0)
        section_counts[category] += 1
        if is_correct:
            section_scores[category] += 1

    score = max(0, min(100, round((total / max(1, len(questions))) * 100, 2)))
    accuracy = round((correct / max(1, attempted)) * 100, 2) if attempted else 0
    strengths = []
    weaknesses = []
    for category in section_scores:
        pct = round((section_scores[category] / max(1, section_counts[category])) * 100, 2)
        if pct >= 70:
            strengths.append(_category_title(category))
        elif pct < 50:
            weaknesses.append(_category_title(category))

    readiness = min(100, max(0, score))
    if readiness >= 90:
        readiness_label = "Highly Placement Ready"
    elif readiness >= 75:
        readiness_label = "Placement Ready"
    elif readiness >= 60:
        readiness_label = "Developing"
    elif readiness >= 40:
        readiness_label = "Needs Improvement"
    else:
        readiness_label = "Beginner"

    return {
        "overall_score": score,
        "accuracy": accuracy,
        "correct": correct,
        "incorrect": incorrect,
        "attempted": attempted,
        "readiness": readiness,
        "readiness_label": readiness_label,
        "strengths": strengths or ["General aptitude foundation"],
        "weaknesses": weaknesses or ["Need more focused revision"],
        "section_scores": {key: round((value / max(1, count)) * 100, 2) for key, value in section_scores.items() for count in [section_counts.get(key, 1)]},
    }


class AssessmentStartRequest(BaseModel):
    sections: Optional[List[str]] = None
    duration_minutes: int = 60
    total_questions: int = 20


class AssessmentAnswerRequest(BaseModel):
    assessment_id: int
    question_id: str
    selected_option: str


class CodingRunRequest(BaseModel):
    problem_id: int
    language: str = "Python"
    code: str


@router.get("/categories")
def practice_categories():
    return {
        "categories": [
            {"key": "communication", "label": "Communication", "description": "Grammar, vocabulary, sentence correction and workplace communication"},
            {"key": "aptitude", "label": "Quantitative Aptitude", "description": "Percentages, averages, profit and loss, ratio, probability and arithmetic"},
            {"key": "logical", "label": "Logical Ability", "description": "Series, puzzles, coding-decoding, syllogisms and deduction"},
            {"key": "reasoning", "label": "Reasoning", "description": "Seating arrangements, ranking, pattern analysis and logical puzzles"},
            {"key": "technical", "label": "Technical MCQ", "description": "Java, SQL, DBMS, DSA, OS, HTML, CSS and core computer science"},
        ]
    }


@router.get("/questions")
def practice_questions(category: str = "technical", limit: int = 10, difficulty: str = "all", db: Session = Depends(get_db)):
    questions = _pick_questions(category, limit)
    return {"category": category, "count": len(questions), "questions": questions}


@router.post("/assessments/start")
def start_assessment(req: AssessmentStartRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sections = req.sections or ["communication", "aptitude", "logical", "reasoning", "technical"]
    questions: List[Dict[str, Any]] = []
    for section in sections:
        questions.extend({**question, "category": section} for question in _pick_questions(section, max(3, min(10, req.total_questions // max(1, len(sections))))))

    if not questions:
        raise HTTPException(status_code=400, detail="No questions available for the selected sections.")

    assessment = PracticeAssessment(
        user_id=current_user.id,
        title="Placement Assessment",
        sections=sections,
        total_questions=len(questions),
        duration_minutes=req.duration_minutes,
        status="active",
        questions_json=questions,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return {
        "assessment_id": assessment.id,
        "title": assessment.title,
        "sections": sections,
        "total_questions": len(questions),
        "duration_minutes": assessment.duration_minutes,
        "questions": questions,
    }


@router.post("/assessments/answer")
def submit_assessment_answer(req: AssessmentAnswerRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assessment = db.query(PracticeAssessment).filter(PracticeAssessment.id == req.assessment_id, PracticeAssessment.user_id == current_user.id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    question = next((item for item in assessment.questions_json if item.get("id") == req.question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found in this assessment.")
    is_correct = str(req.selected_option or "").upper() == str(question.get("correct_answer") or "").upper()
    answer = PracticeAnswer(
        assessment_id=assessment.id,
        question_id=req.question_id,
        question_category=str(question.get("category") or "technical"),
        selected_option=req.selected_option,
        correct_option=question.get("correct_answer"),
        is_correct=is_correct,
        marks=float(question.get("marks", 1)) if is_correct else -float(question.get("negative_marks", 0.25)),
    )
    db.add(answer)
    db.commit()
    return {
        "question_id": req.question_id,
        "result": "correct" if is_correct else "incorrect",
        "correct_answer": question.get("correct_answer"),
        "explanation": question.get("explanation"),
    }


@router.post("/assessments/submit")
def submit_assessment(payload: Dict[str, Any], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assessment_id = payload.get("assessment_id")
    responses = payload.get("responses") or {}
    assessment = db.query(PracticeAssessment).filter(PracticeAssessment.id == assessment_id, PracticeAssessment.user_id == current_user.id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")

    questions = assessment.questions_json or []
    result = _build_result(questions, responses)
    assessment.status = "completed"
    assessment.score = result["overall_score"]
    assessment.readiness = result["readiness"]
    assessment.result_json = result
    assessment.completed_at = datetime.utcnow()
    db.commit()

    history = PracticePerformance(
        user_id=current_user.id,
        assessment_name=assessment.title,
        overall_score=result["overall_score"],
        readiness=result["readiness"],
        section_scores=result["section_scores"],
        coding_score=0.0,
        tests_completed=1,
    )
    db.add(history)
    db.commit()

    for question in questions:
        response = responses.get(str(question["id"])) or responses.get(question["id"])
        if response is None:
            continue
        selected = str(response.get("selected_option") or "").upper()
        correct = str(question.get("correct_answer") or "").upper()
        mark = float(question.get("marks", 1)) if selected == correct else -float(question.get("negative_marks", 0.25))
        db.add(PracticeAnswer(
            assessment_id=assessment.id,
            question_id=str(question["id"]),
            question_category=str(question.get("category") or "technical"),
            selected_option=selected,
            correct_option=correct,
            is_correct=(selected == correct),
            marks=mark,
        ))
    db.commit()

    return {
        "assessment_id": assessment.id,
        "status": "completed",
        "result": result,
        "recommendations": _recommendations(result["weaknesses"], result["strengths"]),
    }


@router.get("/assessments/{assessment_id}/result")
def get_assessment_result(assessment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assessment = db.query(PracticeAssessment).filter(PracticeAssessment.id == assessment_id, PracticeAssessment.user_id == current_user.id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    return {"assessment_id": assessment.id, "result": assessment.result_json or {"overall_score": assessment.score, "readiness": assessment.readiness}}


@router.get("/history")
def practice_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(PracticeAssessment).filter(PracticeAssessment.user_id == current_user.id).order_by(PracticeAssessment.created_at.desc()).all()
    return [{
        "assessment_id": item.id,
        "title": item.title,
        "score": item.score,
        "readiness": item.readiness,
        "sections": item.sections,
        "status": item.status,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    } for item in items]


@router.get("/performance")
def practice_performance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(PracticePerformance).filter(PracticePerformance.user_id == current_user.id).order_by(PracticePerformance.created_at.desc()).all()
    if not items:
        return {"overall_score": 0, "tests_completed": 0, "readiness": 0, "average_accuracy": 0, "history": []}

    avg_score = sum(item.overall_score for item in items) / len(items)
    avg_ready = sum(item.readiness for item in items) / len(items)
    return {
        "overall_score": round(avg_score, 2),
        "tests_completed": len(items),
        "readiness": round(avg_ready, 2),
        "average_accuracy": round(avg_score, 2),
        "history": [{
            "assessment_name": item.assessment_name,
            "overall_score": item.overall_score,
            "readiness": item.readiness,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        } for item in items],
    }


@router.get("/coding/problems")
def get_coding_problems(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    problems = db.query(PracticeCodingProblem).order_by(PracticeCodingProblem.id.asc()).all()
    if not problems:
        for problem in CODING_PROBLEMS:
            db.add(PracticeCodingProblem(
                title=problem["title"],
                topic=problem["topic"],
                difficulty=problem["difficulty"],
                description=problem["description"],
                input_format=problem["input_format"],
                output_format=problem["output_format"],
                constraints=problem["constraints"],
                example_input=problem["example_input"],
                example_output=problem["example_output"],
                template=problem["template"],
                tags=problem.get("tags", [problem["topic"]]),
                public_test_cases=problem.get("public_test_cases", []),
                hidden_test_cases=problem.get("hidden_test_cases", []),
                time_limit_ms=problem.get("time_limit_ms", 1000),
                memory_limit_mb=problem.get("memory_limit_mb", 256),
                supported_languages=problem.get("supported_languages", ["Python"]),
            ))
        db.commit()
        problems = db.query(PracticeCodingProblem).order_by(PracticeCodingProblem.id.asc()).all()
    return {"problems": [{
        "id": item.id,
        "title": item.title,
        "topic": item.topic,
        "difficulty": item.difficulty,
        "description": item.description,
        "input_format": item.input_format,
        "output_format": item.output_format,
        "constraints": item.constraints,
        "example_input": item.example_input,
        "example_output": item.example_output,
        "template": item.template,
        "supported_languages": item.supported_languages or ["Python"],
        "public_test_cases": item.public_test_cases or [],
    } for item in problems]}


@router.get("/coding/problems/{problem_id}")
def get_coding_problem(problem_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    problem = db.query(PracticeCodingProblem).filter(PracticeCodingProblem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Coding problem not found.")
    return {
        "id": problem.id,
        "title": problem.title,
        "topic": problem.topic,
        "difficulty": problem.difficulty,
        "description": problem.description,
        "input_format": problem.input_format,
        "output_format": problem.output_format,
        "constraints": problem.constraints,
        "example_input": problem.example_input,
        "example_output": problem.example_output,
        "template": problem.template,
        "supported_languages": problem.supported_languages or ["Python"],
        "public_test_cases": problem.public_test_cases or [],
    }


@router.post("/coding/run")
def run_code(req: CodingRunRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    problem = db.query(PracticeCodingProblem).filter(PracticeCodingProblem.id == req.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")

    tests = problem.public_test_cases or []
    language = req.language or "Python"
    result = _execute_code(language, req.code, tests)
    return result


@router.post("/coding/submit")
def submit_code(req: CodingRunRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    problem = db.query(PracticeCodingProblem).filter(PracticeCodingProblem.id == req.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")
    all_tests = (problem.public_test_cases or []) + (problem.hidden_test_cases or [])
    result = _execute_code(req.language or "Python", req.code, all_tests)
    submission = PracticeCodingSubmission(
        user_id=current_user.id,
        problem_id=problem.id,
        language=req.language or "Python",
        code=req.code,
        status="accepted" if result.get("passed") else "wrong_answer",
        score=result.get("score", 0),
        passed_cases=result.get("passed_cases", 0),
        total_cases=result.get("total_cases", 0),
        execution_time_ms=result.get("execution_time_ms", 0),
        output=result.get("output", ""),
        feedback=result.get("feedback", ""),
    )
    db.add(submission)
    db.commit()
    return result


@router.get("/recommendations")
def get_recommendations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assessments = db.query(PracticeAssessment).filter(PracticeAssessment.user_id == current_user.id).order_by(PracticeAssessment.created_at.desc()).all()
    if not assessments:
        return {"recommendations": [
            {"category": "technical", "title": "Strengthen Data Structures", "description": "Practice arrays, strings, and hash maps before your next test."},
            {"category": "aptitude", "title": "Improve Quantitative Aptitude", "description": "Work on percentages, ratio, simple interest, and time-speed-distance questions."},
        ]}

    latest = assessments[0].result_json or {}
    weak = latest.get("weaknesses") or ["Technical MCQ"]
    recs = []
    for topic in weak[:3]:
        if "Technical" in topic or "Java" in topic:
            recs.append({"category": "technical", "title": f"Practice {topic}", "description": "Solve a focused set of problems around Java, SQL, and data structures."})
        elif "Quant" in topic or "Aptitude" in topic:
            recs.append({"category": "aptitude", "title": "Quantitative Aptitude", "description": "Work on percentages, averages, SI/CI, ratio and time-speed-distance sets."})
        else:
            recs.append({"category": "communication", "title": "Improve communication skills", "description": "Practice grammar, sentence correction, vocabulary, and professional email writing."})
    return {"recommendations": recs[:4]}


def _execute_code(language: str, code: str, tests: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not tests:
        return {"passed": False, "score": 0, "passed_cases": 0, "total_cases": 0, "feedback": "No test cases available", "output": ""}

    lang = (language or "Python").lower()
    if "python" in lang:
        try:
            namespace = {}
            exec(code, namespace)
            match_func = None
            for name, value in namespace.items():
                if callable(value):
                    match_func = value
                    break
            if not match_func:
                return {"passed": False, "score": 0, "passed_cases": 0, "total_cases": len(tests), "feedback": "No callable function found in the submitted code.", "output": ""}

            passed = 0
            output = ""
            for idx, test_case in enumerate(tests, start=1):
                input_value = test_case.get("input")
                expected = str(test_case.get("output") or "").strip()
                try:
                    if isinstance(input_value, str) and input_value.strip() and "\n" in input_value:
                        result = match_func(input_value)
                    else:
                        result = match_func(input_value)
                    result_value = str(result).strip()
                    if result_value == expected:
                        passed += 1
                    else:
                        output = f"Test case {idx} failed: expected {expected}, got {result_value}"
                        break
                except Exception as exc:
                    output = f"Runtime error in case {idx}: {exc}"
                    break
            score = round((passed / len(tests)) * 100, 2)
            return {
                "passed": passed == len(tests),
                "score": score,
                "passed_cases": passed,
                "total_cases": len(tests),
                "execution_time_ms": 0,
                "output": output or "Execution succeeded.",
                "feedback": "All public tests passed." if passed == len(tests) else f"Passed {passed}/{len(tests)} test cases.",
            }
        except Exception as exc:
            return {"passed": False, "score": 0, "passed_cases": 0, "total_cases": len(tests), "feedback": f"Compilation/runtime error: {exc}", "output": str(exc)}

    return {"passed": False, "score": 0, "passed_cases": 0, "total_cases": len(tests), "feedback": "Only Python execution is enabled in the current sandboxed runtime.", "output": ""}


def _recommendations(weaknesses: List[str], strengths: List[str]) -> List[str]:
    base = []
    if any("aptitude" in item.lower() for item in weaknesses):
        base.append("Practice percentages, ratio and time-speed-distance questions.")
    if any("technical" in item.lower() or "java" in item.lower() or "sql" in item.lower() for item in weaknesses):
        base.append("Revise Java collections, SQL joins, and DBMS fundamentals.")
    if any("communication" in item.lower() for item in weaknesses):
        base.append("Work on sentence correction, grammar, and professional email writing.")
    if not base:
        base.append("Continue regular practice and attempt one more mock assessment to consolidate your gains.")
    return base
