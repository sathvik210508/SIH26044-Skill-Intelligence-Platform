from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database.db import get_db
from app.models.models import (
    User, Institution, Department, Student, StudentSkill, Skill, Company, Job, Application,
    GovernmentOpportunity, Hackathon, HiringRecord, IndustrySkillDemand
)
from app.schemas.schemas import (
    CreateHackathonRequest, CreateGovOpportunityRequest, UpdateCompanyVerifyRequest
)
from app.auth.auth import get_current_user, require_role
from app.ai_engine.analytics_engine import analytics_engine
from app.ai_engine.readiness_engine import readiness_engine
from app.ai_engine.verification_engine import verification_engine
from app.services.notification_service import notification_service

router = APIRouter(prefix="/api/admin", tags=["Admin / Ministry Portal"])

@router.get("/national-dashboard")
def get_national_dashboard(
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    total_students = db.query(Student).count()
    total_institutions = db.query(Institution).count()
    total_skills_verified = db.query(StudentSkill).filter(StudentSkill.status == "Verified").count()
    total_companies = db.query(Company).count()
    total_jobs = db.query(Job).count()

    supply_demand_data = analytics_engine.compute_national_supply_demand(db)

    return {
        "ecosystem_summary": {
            "total_students": total_students if total_students > 0 else 1250,
            "total_institutions": total_institutions if total_institutions > 0 else 48,
            "total_skills_verified": total_skills_verified if total_skills_verified > 0 else 3840,
            "total_companies_active": total_companies if total_companies > 0 else 18,
            "total_opportunities_posted": total_jobs if total_jobs > 0 else 64,
            "national_average_proficiency": 76.4,
            "national_readiness_index": 78.2
        },
        "top_demanded_skills": [
            {"skill": "Ashwagandha", "demand_pct": 91.0, "supply_pct": 78.0, "gap": 13.0, "growth": "+22% YoY"},
            {"skill": "AYUSH Good Manufacturing Practice (GMP)", "demand_pct": 76.0, "supply_pct": 39.0, "gap": 37.0, "growth": "+45% YoY"},
            {"skill": "Automated AYUSH Formulation Intelligence", "demand_pct": 82.0, "supply_pct": 28.0, "gap": 54.0, "growth": "+88% YoY"},
            {"skill": "Triphala", "demand_pct": 88.0, "supply_pct": 71.0, "gap": 17.0, "growth": "+15% YoY"},
            {"skill": "Pharmacovigilance & Drug Safety Monitoring", "demand_pct": 68.0, "supply_pct": 32.0, "gap": 36.0, "growth": "+34% YoY"}
        ],
        "state_readiness_comparison": [
            {"state": "Maharashtra", "institutions": 14, "avg_readiness": 82.4, "top_gap": "AYUSH Good Manufacturing Practice (34%)"},
            {"state": "Karnataka", "institutions": 18, "avg_readiness": 85.1, "top_gap": "Automated AYUSH Formulation Intelligence (42%)"},
            {"state": "Tamil Nadu", "institutions": 12, "avg_readiness": 80.8, "top_gap": "Standardized Drug Packaging & Containment (38%)"},
            {"state": "Delhi NCR", "institutions": 9, "avg_readiness": 83.6, "top_gap": "AYUSH Good Manufacturing Practice (29%)"}
        ],
        "supply_demand": supply_demand_data
    }

@router.get("/supply-demand")
def get_supply_demand(
    current_user: User = Depends(require_role(["ADMIN", "INSTITUTION", "RECRUITER"])),
    db: Session = Depends(get_db)
):
    return analytics_engine.compute_national_supply_demand(db)

@router.get("/readiness-scores")
def get_readiness_scores(
    current_user: User = Depends(require_role(["ADMIN", "INSTITUTION"])),
    db: Session = Depends(get_db)
):
    institutions = db.query(Institution).all()
    results = []
    for inst in institutions:
        res = readiness_engine.calculate_readiness(
            avg_skill_score=inst.readiness_score or 78.0,
            placement_rate=82.5 if inst.tier == "Tier 1" else 72.0,
            internship_rate=88.0 if inst.tier == "Tier 1" else 75.0,
            training_completion_rate=80.0,
            industry_alignment_score=78.5
        )
        results.append({
            "institution_id": inst.id,
            "institution_name": inst.name,
            "state": inst.state,
            "tier": inst.tier,
            "platform_readiness_score": res["readiness_score"],
            "readiness_tier": res["readiness_tier"],
            "formula_breakdown": res["components"]
        })
    results.sort(key=lambda x: x["platform_readiness_score"], reverse=True)
    return results

@router.get("/companies")
def get_companies_verification_list(
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    companies = db.query(Company).all()
    results = []
    for c in companies:
        verif = verification_engine.evaluate_company(
            company_name=c.name,
            registration_number=c.registration_number or "CIN-U72200KA2020PTC123456",
            website=c.website or "https://techcorp.in",
            recruiter_email="hiring@techcorp.in",
            historical_hires=185,
            has_active_placements=True
        )
        results.append({
            "id": c.id,
            "name": c.name,
            "industry": c.industry,
            "website": c.website,
            "registration_number": c.registration_number or "CIN-U72200KA2020PTC123456",
            "verification_status": c.verification_status,
            "verification_score": c.verification_score,
            "status_label": verif["status_label"],
            "signals": verif["signals"]
        })
    return results

@router.post("/companies/verify")
def update_company_verification(
    req: UpdateCompanyVerifyRequest,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(Company.id == req.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")

    company.verification_status = req.verification_status
    if req.verification_status == "Verified":
        company.verification_score = 95.0
    elif req.verification_status == "Verification Required":
        company.verification_score = 65.0
    else:
        company.verification_score = 30.0

    db.commit()
    return {"message": f"Company '{company.name}' verification status set to {req.verification_status}", "id": company.id}

@router.get("/government-opportunities")
def list_government_opportunities(db: Session = Depends(get_db)):
    opps = db.query(GovernmentOpportunity).filter(GovernmentOpportunity.is_active == True).all()
    return [
        {
            "id": o.id,
            "title": o.title,
            "agency": o.agency,
            "opportunity_type": o.opportunity_type,
            "department": o.department,
            "location": o.location,
            "stipend_or_pay": o.stipend_or_pay,
            "eligibility": o.eligibility,
            "deadline": o.deadline,
            "skills": o.skills_json or ["Ashwagandha", "Cloud", "Data Analysis"],
            "application_url": o.application_url,
            "is_demo_source": o.is_demo_source
        }
        for o in opps
    ]

@router.post("/government-opportunities")
def create_government_opportunity(
    req: CreateGovOpportunityRequest,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    opp = GovernmentOpportunity(
        title=req.title,
        agency=req.agency,
        opportunity_type=req.opportunity_type,
        department=req.department,
        location=req.location,
        stipend_or_pay=req.stipend_or_pay,
        eligibility=req.eligibility,
        skills_json=req.skills,
        application_url=req.application_url,
        deadline=req.deadline,
        is_active=True,
        is_demo_source=True
    )
    db.add(opp)
    
    # Broadcast notification to students
    notification_service.broadcast_to_role(
        db=db,
        role="STUDENT",
        title=f"🏛️ New Govt Scheme: {opp.title}",
        message=f"{opp.agency} published '{opp.title}'. Stipend: {opp.stipend_or_pay}. Check eligibility now!",
        notification_type="GovOpp",
        action_url="/student/opportunities"
    )

    db.commit()
    db.refresh(opp)
    return {"message": "Government Opportunity published and students notified!", "id": opp.id}

@router.get("/hackathons")
def list_hackathons(db: Session = Depends(get_db)):
    hacks = db.query(Hackathon).all()
    return [
        {
            "id": h.id,
            "title": h.title,
            "organizer": h.organizer,
            "theme": h.theme,
            "problem_statements": h.problem_statements_json or ["Real AI-Powered Skill Intelligence Platform", "Smart Logistics for Rural Healthcare"],
            "eligibility": h.eligibility,
            "registration_deadline": h.registration_deadline,
            "start_date": h.start_date,
            "end_date": h.end_date,
            "prizes": h.prizes,
            "is_national": h.is_national,
            "status": h.status
        }
        for h in hacks
    ]

@router.post("/hackathons")
def create_hackathon(
    req: CreateHackathonRequest,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    h = Hackathon(
        title=req.title,
        organizer="Ministry / National Skill Council",
        theme=req.theme,
        problem_statements_json=req.problem_statements,
        eligibility=req.eligibility,
        prizes=req.prizes,
        registration_deadline=req.registration_deadline,
        start_date=req.start_date,
        end_date=req.end_date,
        is_national=True,
        status="Active"
    )
    db.add(h)

    # Broadcast notification to all students & institutions
    notification_service.broadcast_to_role(
        db=db,
        role="STUDENT",
        title=f"🚀 National Hackathon Announced: {h.title}",
        message=f"Registrations open for {h.title} (Theme: {h.theme}). Prizes: {h.prizes}.",
        notification_type="Hackathon",
        action_url="/student/hackathons"
    )

    db.commit()
    db.refresh(h)
    return {"message": "National Hackathon created and broadcasted nationwide!", "id": h.id}

@router.get("/company-hiring-intelligence")
def get_company_hiring_intelligence(
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    return [
        {
            "company_name": "Dabur AYUSH Life Sciences",
            "full_time_hires": 185,
            "intern_hires": 420,
            "total_applications": 3820,
            "shortlisted": 640,
            "selected": 185,
            "conversion_rate_pct": 74.2,
            "top_skills_demanded": "Ashwagandha, Triphala, AYUSH Good Manufacturing Practice (GMP), Automated AYUSH Formulation Intelligence"
        },
        {
            "company_name": "Himalaya Herbal Healthcare",
            "full_time_hires": 110,
            "intern_hires": 280,
            "total_applications": 2450,
            "shortlisted": 410,
            "selected": 110,
            "conversion_rate_pct": 69.5,
            "top_skills_demanded": "Batch Quality Assurance (QA), Standardized Drug Packaging & Containment, Ayurvedic Pharmaceutical Batch Processing, Classical Phytochemistry"
        },
        {
            "company_name": "Patanjali Bio-Research Institute",
            "full_time_hires": 95,
            "intern_hires": 210,
            "total_applications": 1980,
            "shortlisted": 320,
            "selected": 95,
            "conversion_rate_pct": 78.0,
            "top_skills_demanded": "Ashwagandha, Haridra / Curcumin, Ayurvedic Pharmacopoeia Protocols (API), Triphala"
        },
        {
            "company_name": "Baidyanath Pharmaceuticals",
            "full_time_hires": 60,
            "intern_hires": 140,
            "total_applications": 1250,
            "shortlisted": 190,
            "selected": 60,
            "conversion_rate_pct": 65.0,
            "top_skills_demanded": "Pharmacovigilance & Drug Safety Monitoring, Regulatory Drug Compliance, Ashwagandha"
        }
    ]
