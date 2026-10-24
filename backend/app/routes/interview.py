from datetime import datetime
import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ai.agentic_interview import (
    _extract_profile_from_resume,
    adaptive_difficulty,
    evaluate_answer,
    final_performance_report,
    generate_question_for_session,
    plan_interview,
    run_coding_challenge,
)
from app.database import get_db
from app.models.models import (
    InterviewAnswer,
    InterviewPerformance,
    InterviewQuestion,
    InterviewReport,
    InterviewSession,
    Resume,
    ResumeAnalysis,
    User,
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/interview", tags=["AI Interview Prep"])

BALANCED_SECTION_COUNTS = {
    "communication": 10,
    "aptitude": 10,
    "logical": 10,
    "reasoning": 10,
    "technical": 20,
    "coding": 2,
}


def _build_balanced_sections(selected_sections: List[str], requested_total: int) -> List[str]:
    normalized = [section for section in selected_sections if section and str(section).strip()]
    if not normalized:
        return ["communication", "aptitude", "logical", "reasoning", "technical", "coding"]

    full_sections = ["communication", "aptitude", "logical", "reasoning", "technical", "coding"]
    if len(normalized) >= 5 or set(normalized).issuperset({"communication", "aptitude", "logical", "reasoning", "technical"}):
        return full_sections

    if len(normalized) == 1:
        section = normalized[0]
        if section == "coding":
            return ["coding"]
        if section in BALANCED_SECTION_COUNTS:
            return [section]
        return normalized

    merged = []
    for section in full_sections:
        if section in normalized:
            merged.append(section)
    return merged if merged else normalized


def _section_question_plan(selected_sections: List[str], requested_total: int) -> List[str]:
    section_plan: List[str] = []
    if len(selected_sections) == 1 and selected_sections[0] == "coding":
        return ["coding"] * 2

    if len(selected_sections) == 1:
        section = selected_sections[0]
        base_count = BALANCED_SECTION_COUNTS.get(section, max(10, min(25, requested_total)))
        return [section] * max(1, base_count)

    for section in selected_sections:
        if section == "coding":
            section_plan.extend(["coding"] * 2)
            continue
        section_plan.extend([section] * BALANCED_SECTION_COUNTS.get(section, max(10, min(25, requested_total))))
    return section_plan


class InterviewSetupRequest(BaseModel):
    target_role: str = "Java Backend Developer"
    interview_type: str = "technical"
    difficulty: str = "intermediate"
    question_count: int = 10
    job_description: Optional[str] = None
    coding_language: Optional[str] = "Java"
    sections: Optional[list[str]] = None


class InterviewAnswerRequest(BaseModel):
    answer: str
    question_number: Optional[int] = None


class LegacyQuestionGenRequest(BaseModel):
    target_role: Optional[str] = "Software Engineer"
    question_count: int = 12


class LegacyAnswerEvalRequest(BaseModel):
    question: str
    answer: str


def _load_resume_context(current_user: User, db: Session):
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.user_id == current_user.id).order_by(ResumeAnalysis.created_at.desc()).first()

    profile = _extract_profile_from_resume(current_user, db)
    target_role = profile.get("target_role") or (analysis.target_role if analysis else "Software Engineer")
    skill_list = profile.get("skills") or ["Java", "SQL", "REST API", "Docker"]
    missing = profile.get("missing_skills") or []
    if not missing:
        missing = ["Spring Boot", "Hibernate", "REST API", "Docker"]
    return profile, skill_list, target_role, missing


@router.post("/generate")
def get_interview_questions(req: LegacyQuestionGenRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile, skills, target_role, missing = _load_resume_context(current_user, db)
    target_role = req.target_role or target_role
    plan = plan_interview(profile, target_role, "technical", "intermediate", max(5, min(20, req.question_count)))
    generated = {
        "questions": [],
        "plan": plan,
    }
    for i in range(1, min(10, max(3, req.question_count)) + 1):
        q = generate_question_for_session({
            "candidate_profile": profile,
            "target_role": target_role,
            "difficulty": "Intermediate",
            "current_question": i,
            "question_history": [],
        })
        generated["questions"].append({
            "id": i,
            "category": q.get("category"),
            "question": q.get("question"),
            "difficulty": q.get("difficulty"),
            "sample_answer": q.get("question"),
        })
    return generated


@router.post("/generate-topic-test")
def get_topic_test(req: LegacyQuestionGenRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile, skills, target_role, missing = _load_resume_context(current_user, db)
    return {
        "questions": [
            {
                "id": 1,
                "category": "Java",
                "question": "Which Java feature helps reduce memory issues in long-running backend services?",
                "options": ["Garbage Collection", "HTML Parsing", "CSS Grid", "REST Routing"],
                "correct_option": 0,
                "explanation": "Garbage Collection is essential to Java runtime memory management.",
                "difficulty": "Intermediate",
            },
            {
                "id": 2,
                "category": "REST API",
                "question": "Which HTTP method is used to update an existing resource?",
                "options": ["GET", "POST", "PUT", "DELETE"],
                "correct_option": 2,
                "explanation": "PUT is commonly used to replace or update an existing resource.",
                "difficulty": "Beginner",
            }
        ]
    }


@router.post("/evaluate")
def evaluate_candidate_answer(req: LegacyAnswerEvalRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not req.answer or len(req.answer.strip()) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please provide a complete answer for evaluation.")
    profile, _, _, _ = _load_resume_context(current_user, db)
    return evaluate_answer(req.question, req.answer, profile)


@router.post("/start")
def start_interview(req: InterviewSetupRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile, _, _, missing = _load_resume_context(current_user, db)
    profile["missing_skills"] = missing
    coding_language = (req.coding_language or "Java").strip().lower()
    if coding_language not in {"python", "java"}:
        raise HTTPException(status_code=400, detail="Coding language must be Python or Java.")
    coding_language = coding_language.title()

    raw_sections = list(req.sections or [req.interview_type]) if req.sections else [req.interview_type]
    selected_sections = [section for section in raw_sections if section and str(section).strip()]
    if req.interview_type == "full-practice" or set(selected_sections) >= {"communication", "aptitude", "logical", "reasoning", "technical"}:
        section_order = ["communication", "aptitude", "logical", "reasoning", "technical"]
        selected_sections = [section for section in section_order if section in selected_sections]
        selected_sections.append("coding")
    else:
        selected_sections = _build_balanced_sections(selected_sections, int(req.question_count or 10))
    if not selected_sections:
        selected_sections = ["communication", "aptitude", "logical", "reasoning", "technical", "coding"]

    effective_type = "mixed-practice" if len(selected_sections) > 1 else selected_sections[0]
    question_plan = _section_question_plan(selected_sections, int(req.question_count or 10))
    total_questions = len(question_plan)
    plan = plan_interview(profile, req.target_role, effective_type, req.difficulty, max(10, min(80, total_questions)), req.job_description)
    session = InterviewSession(
        user_id=current_user.id,
        target_role=req.target_role,
        interview_type=effective_type,
        difficulty=req.difficulty,
        total_questions=total_questions,
        status="active",
        current_question=1,
        session_data={"plan": plan, "job_description": req.job_description, "questions": {}, "coding_language": coding_language, "sections": selected_sections, "question_plan": question_plan},
    )
    db.add(session)
    db.flush()

    question_bank = {}
    for index, section_name in enumerate(question_plan, start=1):
        generated = generate_question_for_session({
            "candidate_profile": profile,
            "target_role": req.target_role,
            "interview_type": section_name,
            "difficulty": req.difficulty,
            "current_question": index,
            "question_history": [],
            "coding_language": coding_language,
        })
        question_bank[str(index)] = {
            "question": generated.get("question"),
            "options": generated.get("options") or [],
            "correct_option": generated.get("correct_option"),
            "explanation": generated.get("explanation"),
            "category": generated.get("category"),
            "difficulty": generated.get("difficulty"),
            "topic": generated.get("topic"),
            "question_type": generated.get("question_type") or ("coding" if section_name == "coding" else "mcq"),
            "language": generated.get("language") or ("Java" if section_name == "coding" else None),
            "starter_code": generated.get("starter_code") or "",
            "function_name": generated.get("function_name"),
            "test_cases": generated.get("test_cases") or [],
            "section": section_name,
        }
        question = InterviewQuestion(
            session_id=session.id,
            question_number=index,
            question=generated.get("question"),
            category=generated.get("category"),
            difficulty=generated.get("difficulty"),
            topic=generated.get("topic"),
        )
        db.add(question)
    session.session_data = {"plan": plan, "job_description": req.job_description, "questions": question_bank, "coding_language": coding_language, "sections": selected_sections, "question_plan": question_plan}
    db.commit()
    db.refresh(session)

    section_totals = {section: question_plan.count(section) for section in sorted(set(question_plan))}
    return {
        "session_id": session.id,
        "target_role": session.target_role,
        "interview_type": session.interview_type,
        "difficulty": session.difficulty,
        "total_questions": session.total_questions,
        "current_question": 1,
        "plan": plan,
        "question_plan": question_plan,
        "section_totals": section_totals,
    }


@router.get("/{session_id}/questions")
def get_interview_questions(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session.id
    ).order_by(InterviewQuestion.question_number.asc()).all()
    answers = db.query(InterviewAnswer).filter(InterviewAnswer.session_id == session.id).all()
    answers_by_question = {answer.question_id: answer.answer for answer in answers}
    question_meta = (session.session_data or {}).get("questions", {})
    return {
        "session_id": session.id,
        "total_questions": session.total_questions,
        "status": session.status,
        "questions": [
            {
                "question_number": question.question_number,
                "section": question_meta.get(str(question.question_number), {}).get("section") or question.category or "General",
                "answered": question.id in answers_by_question,
                "answer": answers_by_question.get(question.id),
            }
            for question in questions
        ],
    }


@router.get("/{session_id}/current-question")
def get_current_question(
    session_id: int,
    question_number: Optional[int] = Query(None, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if session.status == "completed":
        return {"session_id": session.id, "has_question": False, "status": "completed", "message": "Interview completed"}
    requested_question_number = question_number or session.current_question
    question = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id, InterviewQuestion.question_number == requested_question_number).first()
    if not question:
        question = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id).order_by(InterviewQuestion.question_number.asc()).first()
    if not question:
        return {"session_id": session.id, "has_question": False, "message": "No questions found"}
    answered_count = db.query(InterviewAnswer).filter(InterviewAnswer.session_id == session.id).count()
    progress = round((answered_count / max(1, session.total_questions)) * 100, 2)
    question_meta = (session.session_data or {}).get("questions", {}).get(str(question.question_number), {})
    saved_answer = db.query(InterviewAnswer).filter(
        InterviewAnswer.session_id == session.id,
        InterviewAnswer.question_id == question.id,
    ).order_by(InterviewAnswer.created_at.desc()).first()
    return {
        "session_id": session.id,
        "question_number": question.question_number,
        "question": question.question,
        "category": question.category,
        "difficulty": question.difficulty,
        "topic": question.topic,
        "section": question_meta.get("section") or question.category,
        "options": question_meta.get("options") or [],
        "question_type": question_meta.get("question_type") or "mcq",
        "language": question_meta.get("language") or "Python",
        "starter_code": question_meta.get("starter_code") or "",
        "function_name": question_meta.get("function_name"),
        "explanation": question_meta.get("explanation") or "",
        "test_cases": question_meta.get("test_cases") or [],
        "progress": progress,
        "total_questions": session.total_questions,
        "status": session.status,
        "saved_answer": saved_answer.answer if saved_answer else None,
    }


@router.post("/{session_id}/run-code")
def run_session_code(session_id: int, body: Dict[str, Any], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    current_question_number = int(body.get("question_number") or session.current_question or 1)
    question = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id, InterviewQuestion.question_number == current_question_number).first()
    if not question:
        raise HTTPException(status_code=404, detail="Current coding question not found")

    meta = (session.session_data or {}).get("questions", {}).get(str(current_question_number), {})
    if not meta or meta.get("question_type") != "coding":
        raise HTTPException(status_code=400, detail="This question is not a coding challenge.")

    code = (body.get("code") or "").strip()
    if not code:
        raise HTTPException(status_code=400, detail="Please write code before running it.")

    result = run_coding_challenge(meta.get("language") or "Python", code, meta)
    return {
        "status": "success" if result.get("passed") else "failed",
        "passed": bool(result.get("passed")),
        "score": float(result.get("score", 0) or 0),
        "passed_cases": int(result.get("passed_cases", 0) or 0),
        "total_cases": int(result.get("total_cases", 0) or 0),
        "feedback": result.get("feedback") or "Code executed.",
        "output": result.get("output") or "",
        "test_cases": meta.get("test_cases") or [],
    }


@router.post("/{session_id}/answer")
def submit_answer(session_id: int, req: InterviewAnswerRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if not req.answer or len(req.answer.strip()) < 1:
        raise HTTPException(status_code=400, detail="Please provide an answer before submitting.")

    question = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id).order_by(InterviewQuestion.question_number.asc()).all()
    target_question = None
    if req.question_number:
        target_question = next((q for q in question if q.question_number == req.question_number), None)
    else:
        target_question = next((q for q in question if q.question_number == session.current_question), None)
    if not target_question:
        raise HTTPException(status_code=404, detail="Current question not found")

    profile, _, _, _ = _load_resume_context(current_user, db)

    question_meta = (session.session_data or {}).get("questions", {}).get(str(target_question.question_number), {})
    correct_option = question_meta.get("correct_option")
    selected_answer = str(req.answer).strip().upper()

    if question_meta.get("question_type") == "coding":
        coding_result = run_coding_challenge(question_meta.get("language") or "Python", req.answer, question_meta)
        passed_cases = int(coding_result.get("passed_cases", 0) or 0)
        total_cases = int(coding_result.get("total_cases", 0) or 0)
        score_value = float(coding_result.get("score", 0) or 0)
        evaluation = {
            "score": score_value,
            "max_score": 10,
            "technical_correctness": score_value,
            "completeness": min(10.0, score_value),
            "relevance": min(10.0, score_value),
            "clarity": min(10.0, max(4.0, score_value / 1.2)),
            "strengths": ["The code compiled and passed the provided test cases." if coding_result.get("passed") else "The logic is close, but at least one test case still fails."],
            "weaknesses": ["Review edge cases and verify your function contract against the challenge requirement." if not coding_result.get("passed") else "Keep practicing more coding patterns and edge cases."],
            "missing_points": [question_meta.get("explanation") or "Check the function logic against all input edge cases."],
            "feedback": coding_result.get("feedback") or "Review the function logic and test edge cases before submitting again.",
            "difficulty_for_next_question": "medium",
            "topic": target_question.topic or question_meta.get("category") or "Coding",
            "recommended_next_action": "moderate_followup",
            "passed_cases": passed_cases,
            "total_cases": total_cases,
            "status": "passed" if coding_result.get("passed") else "failed",
        }
        score = float(evaluation.get("score", 0) or 0)
    elif correct_option:
        is_correct = selected_answer == str(correct_option).upper()
        score = 10.0 if is_correct else 3.0
        evaluation = {
            "score": score,
            "max_score": 10,
            "technical_correctness": score,
            "completeness": 10.0 if is_correct else 4.0,
            "relevance": 10.0 if is_correct else 5.0,
            "clarity": 10.0 if is_correct else 6.0,
            "strengths": ["Correct option selected." if is_correct else "You can improve by reviewing the concept again."],
            "weaknesses": ["Review the concept and try the next one carefully." if not is_correct else "Keep applying the same approach to similar questions."],
            "missing_points": [question_meta.get("explanation") or "Review the key concept and practice similar questions."],
            "feedback": (f"Correct! {question_meta.get('explanation', 'Good answer.')}" if is_correct else f"Not quite. {question_meta.get('explanation', 'Review the concept and try the next question again.')}" ) ,
            "difficulty_for_next_question": "medium",
            "topic": target_question.topic or question_meta.get("category") or "General",
            "recommended_next_action": "moderate_followup",
        }
    else:
        evaluation = evaluate_answer(target_question.question, req.answer, profile)
        score = float(evaluation.get("score", 0) or 0)

    answer_record = db.query(InterviewAnswer).filter(
        InterviewAnswer.session_id == session.id,
        InterviewAnswer.question_id == target_question.id,
    ).order_by(InterviewAnswer.created_at.desc()).first()
    if answer_record is None:
        answer_record = InterviewAnswer(
            question_id=target_question.id,
            session_id=session.id,
            answer=req.answer,
        )
        db.add(answer_record)
    answer_record.answer = req.answer
    answer_record.score = score
    answer_record.technical_score = float(evaluation.get("technical_correctness", score or 0))
    answer_record.clarity_score = float(evaluation.get("clarity", score or 0))
    answer_record.completeness_score = float(evaluation.get("completeness", score or 0))
    answer_record.relevance_score = float(evaluation.get("relevance", score or 0))
    answer_record.feedback = evaluation.get("feedback")
    db.commit(); db.refresh(answer_record)

    performance = db.query(InterviewPerformance).filter(InterviewPerformance.session_id == session.id, InterviewPerformance.topic == (target_question.topic or "General")).first()
    if not performance:
        performance = InterviewPerformance(session_id=session.id, topic=target_question.topic or "General", questions_attempted=0, score=0.0)
        db.add(performance)
    topic_answers = db.query(InterviewAnswer).join(InterviewQuestion).filter(
        InterviewAnswer.session_id == session.id,
        InterviewQuestion.topic == (target_question.topic or "General"),
    ).all()
    performance.questions_attempted = len(topic_answers)
    performance.score = sum(item.score or 0 for item in topic_answers) / max(1, len(topic_answers))
    if performance.score >= 80:
        performance.strength_level = "strong"
    elif performance.score >= 60:
        performance.strength_level = "moderate"
    else:
        performance.strength_level = "weak"
    db.commit()

    session.current_question = min(session.total_questions, (target_question.question_number + 1))
    all_questions_answered = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session.id,
        ~InterviewQuestion.id.in_(
            db.query(InterviewAnswer.question_id).filter(InterviewAnswer.session_id == session.id)
        ),
    ).count() == 0
    session.overall_score = db.query(func.avg(InterviewAnswer.score)).filter(
        InterviewAnswer.session_id == session.id
    ).scalar() or 0.0
    session.difficulty = adaptive_difficulty([score], session.difficulty)
    if all_questions_answered:
        session.status = "completed"
    db.commit()

    next_question = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session.id,
        InterviewQuestion.question_number == target_question.question_number + 1,
    ).first()
    next_meta = (session.session_data or {}).get("questions", {}).get(str(next_question.question_number), {}) if next_question else {}
    return {
        "session_id": session.id,
        "question_number": target_question.question_number,
        "evaluation": evaluation,
        "next_question": {
            "question_number": next_question.question_number if next_question else None,
            "question": next_question.question if next_question else None,
            "category": next_question.category if next_question else None,
            "topic": next_question.topic if next_question else None,
            "section": next_meta.get("section") or (next_question.category if next_question else None),
            "options": next_meta.get("options") or [],
            "question_type": next_meta.get("question_type") or "mcq",
            "language": next_meta.get("language") or "Python",
            "starter_code": next_meta.get("starter_code") or "",
            "function_name": next_meta.get("function_name"),
            "test_cases": next_meta.get("test_cases") or [],
        } if next_question else None,
        "progress": round((db.query(InterviewAnswer).filter(InterviewAnswer.session_id == session.id).count() / max(1, session.total_questions)) * 100, 2),
        "status": session.status,
    }


@router.get("/{session_id}/performance")
def get_performance(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    performance_rows = db.query(InterviewPerformance).filter(InterviewPerformance.session_id == session.id).all()
    return {
        "session_id": session.id,
        "current_score": round(session.overall_score, 2) if session.overall_score else 0,
        "questions_answered": max(0, session.current_question - 1),
        "progress": round((max(0, session.current_question - 1) / max(1, session.total_questions)) * 100, 2),
        "topic_performance": [
            {
                "topic": row.topic,
                "score": round(row.score, 2),
                "questions_attempted": row.questions_attempted,
                "strength_level": row.strength_level,
            } for row in performance_rows
        ],
    }


@router.get("/{session_id}/report")
def get_report(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    report = db.query(InterviewReport).filter(InterviewReport.session_id == session.id).first()
    if report:
        return {
            "session_id": session.id,
            "overall_score": report.overall_score,
            "technical_score": report.technical_score,
            "communication_score": report.communication_score,
            "problem_solving_score": report.problem_solving_score,
            "role_readiness": report.role_readiness,
            "strengths": report.strengths or [],
            "weaknesses": report.weaknesses or [],
            "recommendations": report.recommendations or [],
            "learning_plan": report.learning_plan or [],
        }
    history = []
    for question in db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id).order_by(InterviewQuestion.question_number.asc()).all():
        answer = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == question.id).order_by(InterviewAnswer.created_at.desc()).first()
        if answer:
            history.append({
                "topic": question.topic or question.category,
                "score": answer.score,
                "technical_score": answer.technical_score,
                "clarity_score": answer.clarity_score,
                "question": question.question,
                "evaluation": {
                    "score": answer.score,
                    "technical_score": answer.technical_score,
                    "clarity_score": answer.clarity_score,
                }
            })
    generated_report = final_performance_report({"question_history": history})
    return {
        "session_id": session.id,
        "overall_score": generated_report.get("overall_score", 0),
        "technical_score": generated_report.get("technical_score", 0),
        "communication_score": generated_report.get("communication_score", 0),
        "problem_solving_score": generated_report.get("problem_solving_score", 0),
        "role_readiness": generated_report.get("role_readiness", 0),
        "strengths": generated_report.get("strengths", []),
        "weaknesses": generated_report.get("weaknesses", []),
        "recommendations": generated_report.get("recommendations", []),
        "learning_plan": generated_report.get("learning_plan", []),
    }


@router.get("/history")
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(InterviewSession).filter(InterviewSession.user_id == current_user.id).order_by(InterviewSession.started_at.desc()).all()
    result = []
    for session in sessions:
        result.append({
            "id": session.id,
            "target_role": session.target_role,
            "interview_type": session.interview_type,
            "difficulty": session.difficulty,
            "score": round(session.overall_score, 2),
            "status": session.status,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
        })
    return result


@router.post("/{session_id}/finish")
def finish_interview(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    answers = db.query(InterviewAnswer).filter(InterviewAnswer.session_id == session.id).all()
    history = []
    for answer in answers:
        question = db.query(InterviewQuestion).filter(InterviewQuestion.id == answer.question_id).first()
        history.append({
            "topic": question.topic or question.category or "General",
            "score": answer.score,
            "technical_score": answer.technical_score,
            "clarity_score": answer.clarity_score,
            "question": question.question,
        })

    generated = final_performance_report({"question_history": history})
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    session.overall_score = generated.get("overall_score", 0)
    db.commit()

    report = db.query(InterviewReport).filter(InterviewReport.session_id == session.id).first()
    if not report:
        report = InterviewReport(session_id=session.id)
        db.add(report)
    report.overall_score = generated.get("overall_score", 0)
    report.technical_score = generated.get("technical_score", 0)
    report.communication_score = generated.get("communication_score", 0)
    report.problem_solving_score = generated.get("problem_solving_score", 0)
    report.role_readiness = generated.get("role_readiness", 0)
    report.strengths = generated.get("strengths", [])
    report.weaknesses = generated.get("weaknesses", [])
    report.recommendations = generated.get("recommendations", [])
    report.learning_plan = generated.get("learning_plan", [])
    db.commit()

    return {
        "session_id": session.id,
        "status": session.status,
        "report": {
            "overall_score": report.overall_score,
            "technical_score": report.technical_score,
            "communication_score": report.communication_score,
            "problem_solving_score": report.problem_solving_score,
            "role_readiness": report.role_readiness,
            "strengths": report.strengths,
            "weaknesses": report.weaknesses,
            "recommendations": report.recommendations,
            "learning_plan": report.learning_plan,
        },
    }


@router.post("/weakness-practice")
def weakness_practice(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile, _, target_role, _ = _load_resume_context(current_user, db)
    weak_topics = ["Spring Boot", "Docker", "REST API"]
    session = InterviewSession(
        user_id=current_user.id,
        target_role=target_role,
        interview_type="weakness-practice",
        difficulty="Beginner",
        total_questions=8,
        status="active",
        current_question=1,
        session_data={"weak_topics": weak_topics},
    )
    db.add(session); db.commit(); db.refresh(session)

    for index, topic in enumerate(weak_topics, start=1):
        question = InterviewQuestion(
            session_id=session.id,
            question_number=index,
            question=f"Explain the core concept of {topic} and how it applies to your {target_role} role.",
            category=topic,
            difficulty="Beginner",
            topic=topic,
        )
        db.add(question)
    db.commit()
    return {"session_id": session.id, "message": "Weakness practice session started", "focus_topics": weak_topics}


@router.post("/{session_id}/retake")
def retake_interview(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    original = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Session not found")
    profile, _, _, _ = _load_resume_context(current_user, db)
    retake = InterviewSession(
        user_id=current_user.id,
        target_role=original.target_role,
        interview_type=f"retake-{original.interview_type}",
        difficulty="Intermediate",
        total_questions=max(5, original.total_questions),
        status="active",
        current_question=1,
        session_data={"retake_of": original.id},
    )
    db.add(retake); db.commit(); db.refresh(retake)
    for index in range(1, retake.total_questions + 1):
        generated = generate_question_for_session({
            "candidate_profile": profile,
            "target_role": original.target_role,
            "interview_type": original.interview_type,
            "difficulty": "Intermediate",
            "current_question": index,
            "question_history": [],
        })
        db.add(InterviewQuestion(session_id=retake.id, question_number=index, question=generated.get("question"), category=generated.get("category"), difficulty=generated.get("difficulty"), topic=generated.get("topic")))
    db.commit()
    return {"session_id": retake.id, "message": "Retake session started"}
