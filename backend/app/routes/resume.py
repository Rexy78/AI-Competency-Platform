import json
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from app.database import get_db
from app.models.models import User, Resume, ResumeAnalysis, SkillGap, Recommendation, UserSkill
from app.utils.auth import get_current_user
from app.ai.parser import parse_resume_document
from app.ai.ats_scorer import calculate_ats_score
from app.ai.skill_gap_engine import analyze_skill_gaps
from app.ai.improver import generate_resume_improvements, enhance_single_bullet

router = APIRouter(prefix="/api/resume", tags=["Resume Management & AI"])

UPLOAD_DIR = "./uploaded_resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_and_analyze_resume(
    file: UploadFile = File(...),
    target_role: str = Form("Java Backend Developer"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".docx") or file.filename.endswith(".txt")):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are allowed.")

    file_bytes = await file.read()
    file_path = os.path.join(UPLOAD_DIR, f"{current_user.id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # 1. Parse Resume Document
    parsed_data = parse_resume_document(file_bytes, file.filename)

    # Save Resume Record
    db_resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        raw_text=parsed_data["raw_text"],
        parsed_json=parsed_data
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)

    # 2. Calculate ATS Score
    ats_result = calculate_ats_score(parsed_data, target_role)

    # 3. Analyze Skill Gap & Radar Data
    all_skills = parsed_data["all_skills"]
    gap_result = analyze_skill_gaps(all_skills, target_role)

    # Save Resume Analysis Record
    analysis_record = ResumeAnalysis(
        resume_id=db_resume.id,
        user_id=current_user.id,
        target_role=target_role,
        ats_score=ats_result["ats_score"],
        keyword_score=ats_result["keyword_score"],
        skills_score=ats_result["skills_score"],
        formatting_score=ats_result["formatting_score"],
        experience_score=ats_result["experience_score"],
        section_completeness_score=ats_result["section_completeness_score"],
        suggestions_json=ats_result["suggestions"],
        radar_data_json=gap_result["radar_data"]
    )
    db.add(analysis_record)
    db.commit()
    db.refresh(analysis_record)

    # Save Skill Gaps
    for gap in gap_result["gap_matrix"]:
        db_gap = SkillGap(
            analysis_id=analysis_record.id,
            user_id=current_user.id,
            job_role=target_role,
            skill_name=gap["skill"],
            category=gap["category"],
            status=gap["status"],
            priority=gap["priority"]
        )
        db.add(db_gap)

    # Save Recommendations
    for rec in gap_result["recommendations"]:
        db_rec = Recommendation(
            analysis_id=analysis_record.id,
            user_id=current_user.id,
            skill_name=rec["skill"],
            priority=rec["priority"],
            why_text=rec["why"],
            prerequisites_json=rec["prerequisites"],
            next_steps_json=rec["next_steps"]
        )
        db.add(db_rec)

    # Save User Skills
    for skill_name in all_skills:
        db_skill = UserSkill(
            user_id=current_user.id,
            resume_id=db_resume.id,
            skill_name=skill_name,
            category="Technical"
        )
        db.add(db_skill)

    db.commit()

    return {
        "message": "Resume uploaded and analyzed successfully",
        "resume_id": db_resume.id,
        "analysis_id": analysis_record.id,
        "filename": file.filename,
        "target_role": target_role,
        "parsed_data": parsed_data,
        "ats_result": ats_result,
        "skill_gap_result": gap_result
    }

@router.get("/history")
def get_resume_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    analyses = db.query(ResumeAnalysis).filter(ResumeAnalysis.user_id == current_user.id).order_by(ResumeAnalysis.created_at.desc()).all()
    history = []
    for a in analyses:
        resume = db.query(Resume).filter(Resume.id == a.resume_id).first()
        history.append({
            "analysis_id": a.id,
            "resume_id": a.resume_id,
            "filename": resume.filename if resume else "Resume",
            "target_role": a.target_role,
            "ats_score": a.ats_score,
            "created_at": a.created_at
        })
    return history

@router.get("/analysis/{analysis_id}")
def get_analysis_by_id(analysis_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.id == analysis_id, ResumeAnalysis.user_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found")

    resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()

    return {
        "analysis_id": analysis.id,
        "resume_id": analysis.resume_id,
        "filename": resume.filename if resume else "Resume",
        "target_role": analysis.target_role,
        "ats_score": analysis.ats_score,
        "keyword_score": analysis.keyword_score,
        "skills_score": analysis.skills_score,
        "formatting_score": analysis.formatting_score,
        "experience_score": analysis.experience_score,
        "section_completeness_score": analysis.section_completeness_score,
        "suggestions": analysis.suggestions_json,
        "radar_data": analysis.radar_data_json,
        "parsed_data": resume.parsed_json if resume else {},
        "created_at": analysis.created_at
    }

@router.delete("/analysis/{analysis_id}")
def delete_analysis(analysis_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.id == analysis_id, ResumeAnalysis.user_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found")
    
    db.delete(analysis)
    db.commit()
    return {"message": "Analysis deleted successfully"}

@router.get("/latest")
def get_latest_analysis(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    latest = db.query(ResumeAnalysis).filter(ResumeAnalysis.user_id == current_user.id).order_by(ResumeAnalysis.created_at.desc()).first()
    
    if not latest:
        latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
        if latest_resume:
            return {
                "resume_id": latest_resume.id,
                "filename": latest_resume.filename,
                "parsed_data": latest_resume.parsed_json or {},
                "created_at": latest_resume.created_at
            }
        return {"message": "No analysis found"}

    resume = db.query(Resume).filter(Resume.id == latest.resume_id).first()

    return {
        "analysis_id": latest.id,
        "resume_id": latest.resume_id,
        "filename": resume.filename if resume else "Resume",
        "target_role": latest.target_role,
        "ats_score": latest.ats_score,
        "keyword_score": latest.keyword_score,
        "skills_score": latest.skills_score,
        "formatting_score": latest.formatting_score,
        "experience_score": latest.experience_score,
        "section_completeness_score": latest.section_completeness_score,
        "suggestions": latest.suggestions_json,
        "radar_data": latest.radar_data_json,
        "parsed_data": resume.parsed_json if resume else {},
        "created_at": latest.created_at
    }

@router.post("/improve")
def get_ai_improvements(
    target_role: str = Form("Software Engineer"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    parsed_data = latest_resume.parsed_json if (latest_resume and latest_resume.parsed_json) else {
        "all_skills": ["Java", "JavaScript", "HTML", "CSS", "SQL"],
        "sections": {
            "summary": "Software developer looking for opportunities.",
            "experience": [{"title": "Software Developer"}]
        },
        "personal_info": {"name": current_user.full_name}
    }

    improvements = generate_resume_improvements(parsed_data, target_role)
    return improvements

@router.post("/enhance-bullet")
def enhance_bullet_point(
    text: str = Form(...),
    target_role: str = Form("Software Engineer"),
    current_user: User = Depends(get_current_user)
):
    enhanced = enhance_single_bullet(text, target_role)
    return {"original": text, "enhanced": enhanced}
