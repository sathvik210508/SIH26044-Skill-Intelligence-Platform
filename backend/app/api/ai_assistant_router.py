from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.db import get_db
from app.models.models import User, Workshop, Hackathon
from app.schemas.schemas import AssistantQueryRequest, ConfirmActionRequest
from app.auth.auth import get_current_user
from app.ai_engine.assistant_engine import assistant_engine
from app.services.notification_service import notification_service

router = APIRouter(prefix="/api/ai-assistant", tags=["AI Skill Intelligence Assistant"])

@router.post("/query")
def query_ai_assistant(
    req: AssistantQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = assistant_engine.process_query(
        db=db,
        user=current_user,
        query=req.query,
        active_tab=req.active_tab
    )
    return result

@router.post("/confirm-action")
def confirm_action(
    req: ConfirmActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    role = current_user.role.upper()
    action_type = req.action_type
    params = req.parameters

    if action_type == "CREATE_WORKSHOP":
        if role not in ["INSTITUTION", "ADMIN"]:
            raise HTTPException(status_code=403, detail="Unauthorized to create workshops.")
        
        inst = current_user.institution_profile
        inst_id = inst.id if inst else 1

        w = Workshop(
            institution_id=inst_id,
            title=params.get("title", "Targeted Upskilling Bootcamp"),
            description=params.get("description", "Targeted training program."),
            target_skill_name=params.get("target_skill_name", "AYUSH Good Manufacturing Practice (GMP)"),
            target_department=params.get("target_department", "Dravyaguna Vijnana (Herbal Pharmacology)"),
            target_year=params.get("target_year", 2),
            target_proficiency_max=params.get("target_proficiency_max", 50.0),
            duration_hours=params.get("duration_hours", 24),
            start_date="15 Oct 2026",
            end_date="30 Oct 2026",
            pre_avg_score=38.0,
            post_avg_score=64.0,
            status="Upcoming"
        )
        db.add(w)
        notification_service.broadcast_to_role(
            db=db,
            role="STUDENT",
            title=f"New Workshop: {w.title}",
            message=f"Targeted workshop created for {w.target_skill_name}.",
            notification_type="Workshop"
        )
        db.commit()
        db.refresh(w)
        return {"success": True, "message": f"Successfully created workshop '{w.title}' (ID: {w.id})!", "item_id": w.id}

    elif action_type == "CREATE_HACKATHON":
        if role != "ADMIN":
            raise HTTPException(status_code=403, detail="Unauthorized to create national hackathons.")
        
        h = Hackathon(
            title=params.get("title", "National AI Challenge"),
            organizer="Ministry / National Skill Council",
            theme=params.get("theme", "AI & Innovation"),
            prizes=params.get("prizes", "₹1,50,000"),
            eligibility=params.get("eligibility", "All Students"),
            registration_deadline="15 Nov 2026",
            start_date="20 Nov 2026",
            end_date="22 Nov 2026",
            is_national=True,
            status="Active"
        )
        db.add(h)
        notification_service.broadcast_to_role(
            db=db,
            role="STUDENT",
            title=f"🚀 National Hackathon: {h.title}",
            message="Registrations now open nationwide.",
            notification_type="Hackathon"
        )
        db.commit()
        db.refresh(h)
        return {"success": True, "message": f"Successfully launched National Hackathon '{h.title}' (ID: {h.id})!", "item_id": h.id}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action type '{action_type}'")
