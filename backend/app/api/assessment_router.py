from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database.db import get_db
from app.models.models import User, Student, Skill, AssessmentAttempt
from app.schemas.schemas import SubmitQuizRequest
from app.auth.auth import get_current_user, require_role
from app.services.assessment_service import assessment_service

router = APIRouter(prefix="/api/assessment", tags=["Adaptive Assessments"])

@router.get("/skills")
def list_assessable_skills(db: Session = Depends(get_db)):
    skills = db.query(Skill).all()
    return [{"id": s.id, "name": s.name, "category": s.category, "is_curriculum": s.is_curriculum} for s in skills]

@router.get("/start/{skill_id}")
def start_quiz(
    skill_id: int,
    current_user: User = Depends(require_role(["STUDENT", "ADMIN"])),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    student_id = student.id if student else 1
    quiz_data = assessment_service.generate_adaptive_quiz(
        db=db,
        skill_id=skill_id,
        student_id=student_id,
        num_questions=5
    )
    if "error" in quiz_data:
        raise HTTPException(status_code=404, detail=quiz_data["error"])
    return quiz_data

@router.post("/submit")
def submit_quiz(
    req: SubmitQuizRequest,
    current_user: User = Depends(require_role(["STUDENT"])),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found.")

    result = assessment_service.submit_and_grade_quiz(
        db=db,
        student_id=student.id,
        skill_id=req.skill_id,
        student_answers=req.student_answers,
        answers_key=req.answers_key
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/history")
def get_assessment_history(
    current_user: User = Depends(require_role(["STUDENT"])),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found.")

    attempts = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.student_id == student.id
    ).order_by(AssessmentAttempt.completed_at.desc()).all()

    return [
        {
            "id": a.id,
            "skill_name": db.query(Skill.name).filter(Skill.id == a.skill_id).scalar() or "Technical Skill",
            "score": a.score,
            "passed": a.passed,
            "total_questions": a.total_questions,
            "correct_answers": a.correct_answers,
            "completed_at": a.completed_at.strftime("%d %b %Y, %I:%M %p")
        }
        for a in attempts
    ]
