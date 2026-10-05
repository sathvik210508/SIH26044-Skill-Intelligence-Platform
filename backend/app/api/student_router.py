import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database.db import get_db
from app.models.models import (
    User, Student, StudentSkill, Skill, SkillEvidence, Project, Course, Certification,
    Job, Application, GovernmentOpportunity, Notification
)
from app.schemas.schemas import (
    AddSkillRequest, VerifyExtractedSkillRequest, AddProjectRequest, 
    AddCourseRequest, AddCertRequest, ApplyJobRequest
)
from app.auth.auth import get_current_user, require_role
from app.ai_engine.proficiency_engine import proficiency_engine
from app.ai_engine.matching_engine import matching_engine
from app.ai_engine.gap_analyzer import gap_analyzer
from app.services.resume_extractor import resume_extractor
from app.services.notification_service import notification_service

router = APIRouter(prefix="/api/student", tags=["Student Portal"])

@router.get("/profile")
def get_student_profile(
    current_user: User = Depends(require_role(["STUDENT", "ADMIN", "INSTITUTION", "RECRUITER"])),
    student_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    if student_id and current_user.role in ["ADMIN", "INSTITUTION", "RECRUITER"]:
        student = db.query(Student).filter(Student.id == student_id).first()
    else:
        student = current_user.student_profile
        if not student:
            student = db.query(Student).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    # Format profile response
    skills_data = []
    for s in student.skills:
        skills_data.append({
            "id": s.id,
            "skill_id": s.skill_id,
            "skill_name": s.skill.name,
            "category": s.skill.category,
            "proficiency_score": s.proficiency_score,
            "test_score": s.test_score,
            "practical_score": s.practical_score,
            "verified_score": s.verified_score,
            "course_score": s.course_score,
            "status": s.status,
            "source": s.source,
            "breakdown": s.evidence_breakdown
        })

    return {
        "id": student.id,
        "user_id": student.user_id,
        "full_name": student.user.full_name if student.user else "Student",
        "email": student.user.email if student.user else "",
        "institution_name": student.institution.name if student.institution else "National Institute of Ayurveda (NIA Jaipur)",
        "institution_code": student.institution.code if student.institution else "NIA",
        "department_name": student.department.name if student.department else "Dravyaguna Vijnana (Herbal Pharmacology)",
        "roll_number": student.roll_number or "24NIA001",
        "current_year": student.current_year,
        "cgpa": student.cgpa,
        "career_interests": student.career_interests,
        "bio": student.bio or "Passionate AYUSH pharmaceutical researcher and quality analyst building high-standard herbal formulation systems.",
        "avatar_url": student.avatar_url or "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
        "placement_status": student.placement_status,
        "skills": sorted(skills_data, key=lambda x: x["proficiency_score"], reverse=True),
        "projects": [{"id": p.id, "title": p.title, "description": p.description, "skills_used": p.skills_used, "repo_url": p.repo_url, "live_url": p.live_url} for p in student.projects],
        "courses": [{"id": c.id, "title": c.title, "provider": c.provider, "skills_learned": c.skills_learned, "completion_date": c.completion_date} for c in student.courses],
        "certifications": [{"id": cert.id, "name": cert.name, "issuing_org": cert.issuing_org, "issue_date": cert.issue_date, "credential_id": cert.credential_id} for cert in student.certifications]
    }

@router.post("/add-skill")
def add_student_skill(
    req: AddSkillRequest,
    current_user: User = Depends(require_role(["STUDENT"])),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found.")

    skill_name = req.skill_name.strip()
    skill = db.query(Skill).filter(Skill.name.ilike(skill_name)).first()
    if not skill:
        skill = Skill(name=skill_name, category="General Technical", is_curriculum=False)
        db.add(skill)
        db.flush()

    # Check if student already has this skill
    st_skill = db.query(StudentSkill).filter(
        StudentSkill.student_id == student.id,
        StudentSkill.skill_id == skill.id
    ).first()

    raw_score = req.score or 80.0
    evidence_type = req.evidence_type or "Practical"

    t_score = raw_score if evidence_type == "Test" else (st_skill.test_score if st_skill else None)
    p_score = raw_score if evidence_type == "Practical" else (st_skill.practical_score if st_skill else None)
    v_score = raw_score if evidence_type == "Verified" else (st_skill.verified_score if st_skill else None)
    c_score = raw_score if evidence_type == "Course" else (st_skill.course_score if st_skill else None)

    # Dynamic calculation using central ProficiencyEngine
    calc = proficiency_engine.calculate_proficiency(
        test_score=t_score,
        practical_score=p_score,
        verified_score=v_score,
        course_score=c_score
    )

    if not st_skill:
        st_skill = StudentSkill(
            student_id=student.id,
            skill_id=skill.id,
            test_score=t_score,
            practical_score=p_score,
            verified_score=v_score,
            course_score=c_score,
            proficiency_score=calc["proficiency_score"],
            evidence_breakdown=calc,
            status="Verified",
            source="Manual"
        )
        db.add(st_skill)
        db.flush()
    else:
        st_skill.test_score = t_score
        st_skill.practical_score = p_score
        st_skill.verified_score = v_score
        st_skill.course_score = c_score
        st_skill.proficiency_score = calc["proficiency_score"]
        st_skill.evidence_breakdown = calc
        st_skill.status = "Verified"

    # Add evidence entry
    evidence = SkillEvidence(
        student_skill_id=st_skill.id,
        evidence_type=evidence_type,
        title=f"{evidence_type} Evidence for {skill.name}",
        description=req.description or f"Added by student with initial score of {raw_score}%.",
        url=req.url,
        score_contribution=raw_score,
        is_verified=True
    )
    db.add(evidence)
    db.commit()

    return {
        "message": f"Skill '{skill.name}' added successfully!",
        "skill_id": skill.id,
        "skill_name": skill.name,
        "proficiency_score": calc["proficiency_score"],
        "breakdown": calc["breakdown_explanation"]
    }

@router.post("/resume/extract-skills")
async def extract_resume_skills(
    file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    current_user: User = Depends(require_role(["STUDENT"]))
):
    text = ""
    if file:
        content = await file.read()
        if file.filename.endswith(".pdf"):
            text = resume_extractor.extract_text_from_pdf(content)
        else:
            text = content.decode("utf-8", errors="ignore")
    elif resume_text:
        text = resume_text
    else:
        text = """
        Rahul Sharma | BAMS Ayurvedic Medicine & Pharmaceutical Sciences (3rd Year)
        Skills: Ashwagandha, Triphala, Haridra / Curcumin, Phytochemical Assay & Analysis, Standardized Drug Packaging & Containment, AYUSH Monograph & Batch Record Versioning, Ayurvedic Pharmacopoeia Protocols (API).
        Projects: Phytochemical Standardization Registry built using Ashwagandha, Pharmacopoeia Protocols, and Assay Testing. Ayurvedic Formulation Quality Verification Portal.
        Experience: 3-month AYUSH Pharmaceutical Quality Internship at Dabur Research Labs working with Triphala batch records and Standardized Containment protocols.
        """

    extracted_skills = resume_extractor.extract_skills_from_text(text)
    return {
        "extracted_skills": extracted_skills,
        "skills_count": len(extracted_skills),
        "raw_snippet": text[:300] + "..." if len(text) > 300 else text
    }

@router.post("/resume/verify-skills")
def verify_extracted_skills(
    req: VerifyExtractedSkillRequest,
    current_user: User = Depends(require_role(["STUDENT"])),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found.")

    added_skills = []
    for item in req.skills:
        skill_name = item.get("skill_name")
        verified = item.get("verified", True)
        if not verified or not skill_name:
            continue

        skill = db.query(Skill).filter(Skill.name.ilike(skill_name)).first()
        if not skill:
            skill = Skill(name=skill_name, category="Technical", is_curriculum=False)
            db.add(skill)
            db.flush()

        st_skill = db.query(StudentSkill).filter(
            StudentSkill.student_id == student.id,
            StudentSkill.skill_id == skill.id
        ).first()

        # Resume extraction provides initial verified evidence score (e.g. 75.0)
        v_score = float(item.get("self_rating", 75.0))
        
        t_score = st_skill.test_score if st_skill else None
        p_score = st_skill.practical_score if st_skill else 70.0
        c_score = st_skill.course_score if st_skill else None

        calc = proficiency_engine.calculate_proficiency(
            test_score=t_score,
            practical_score=p_score,
            verified_score=v_score,
            course_score=c_score
        )

        if not st_skill:
            st_skill = StudentSkill(
                student_id=student.id,
                skill_id=skill.id,
                test_score=t_score,
                practical_score=p_score,
                verified_score=v_score,
                course_score=c_score,
                proficiency_score=calc["proficiency_score"],
                evidence_breakdown=calc,
                status="Verified",
                source="Resume_Extraction"
            )
            db.add(st_skill)
            db.flush()
        else:
            st_skill.verified_score = v_score
            st_skill.proficiency_score = calc["proficiency_score"]
            st_skill.evidence_breakdown = calc

        # Add evidence item
        evidence = SkillEvidence(
            student_skill_id=st_skill.id,
            evidence_type="Resume",
            title=f"Extracted & Verified from Resume: {skill.name}",
            description="Verified by student during resume parsing workflow.",
            score_contribution=v_score,
            is_verified=True
        )
        db.add(evidence)
        added_skills.append({
            "skill_name": skill.name,
            "proficiency": calc["proficiency_score"]
        })

    db.commit()
    return {
        "message": f"Successfully verified and imported {len(added_skills)} skills to your profile!",
        "added_skills": added_skills
    }

@router.get("/skill-gaps")
def get_skill_gaps(
    target_role: Optional[str] = "Data Scientist / AI Engineer",
    current_user: User = Depends(require_role(["STUDENT", "ADMIN", "INSTITUTION"])),
    student_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    if student_id and current_user.role in ["ADMIN", "INSTITUTION"]:
        student = db.query(Student).filter(Student.id == student_id).first()
    else:
        student = current_user.student_profile
        if not student:
            student = db.query(Student).first()

    student_skills = {s.skill.name.lower(): s.proficiency_score for s in student.skills} if student else {}
    analysis = gap_analyzer.analyze_student_gaps(student_skills, target_role=target_role)
    return analysis

@router.get("/jobs/matched")
def get_matched_jobs(
    current_user: User = Depends(require_role(["STUDENT", "ADMIN", "RECRUITER"])),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    if not student:
        student = db.query(Student).first()

    student_skills = {s.skill.name.lower(): s.proficiency_score for s in student.skills} if student else {}
    student_cgpa = student.cgpa if student else 8.0
    student_projects = [{"title": p.title} for p in student.projects] if student else []
    student_certs = [{"name": c.name} for c in student.certifications] if student else []

    active_jobs = db.query(Job).filter(Job.is_active == True).all()
    matched_results = []

    for job in active_jobs:
        reqs = []
        for r in job.skill_requirements:
            reqs.append({
                "skill_name": r.skill.name,
                "required_proficiency": r.required_proficiency,
                "importance_weight": r.importance_weight,
                "is_mandatory": r.is_mandatory
            })

        # Central explainable match computation
        match_res = matching_engine.calculate_match(
            student_skills=student_skills,
            job_requirements=reqs,
            student_cgpa=student_cgpa,
            required_cgpa=job.eligibility_cgpa,
            student_projects=student_projects,
            student_certifications=student_certs
        )

        # Check existing application status
        existing_app = db.query(Application).filter(
            Application.job_id == job.id,
            Application.student_id == student.id
        ).first() if student else None

        matched_results.append({
            "job_id": job.id,
            "title": job.title,
            "company_name": job.company.name,
            "company_logo": job.company.logo_url or "https://images.unsplash.com/photo-1549923746-c502d488b3ea?w=100&auto=format&fit=crop&q=80",
            "job_type": job.job_type,
            "location": job.location,
            "salary_range": f"₹{job.salary_min} - ₹{job.salary_max} LPA" if job.salary_min else (job.stipend or "Competitive"),
            "deadline": job.deadline or "Open",
            "eligibility_cgpa": job.eligibility_cgpa,
            "match_score": match_res["match_score"],
            "base_skill_match": match_res["base_skill_match"],
            "critical_coverage_pct": match_res["critical_coverage_pct"],
            "matched_skills": match_res["matched_skills"],
            "skill_gaps": match_res["skill_gaps"],
            "explanation": match_res["explanation"],
            "application_status": existing_app.status if existing_app else "Not Applied",
            "application_id": existing_app.id if existing_app else None
        })

    # Sort jobs by Match Score descending
    matched_results.sort(key=lambda x: x["match_score"], reverse=True)
    return matched_results

@router.post("/apply")
def apply_to_job(
    req: ApplyJobRequest,
    current_user: User = Depends(require_role(["STUDENT"])),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found.")

    job = db.query(Job).filter(Job.id == req.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    # Check if already applied
    existing_app = db.query(Application).filter(
        Application.job_id == req.job_id,
        Application.student_id == student.id
    ).first()

    if existing_app:
        return {"message": "You have already applied for this position.", "status": existing_app.status, "application_id": existing_app.id}

    # Calculate match score
    student_skills = {s.skill.name.lower(): s.proficiency_score for s in student.skills}
    reqs = [{"skill_name": r.skill.name, "required_proficiency": r.required_proficiency, "importance_weight": r.importance_weight} for r in job.skill_requirements]
    
    match_res = matching_engine.calculate_match(
        student_skills=student_skills,
        job_requirements=reqs,
        student_cgpa=student.cgpa,
        required_cgpa=job.eligibility_cgpa
    )

    app_record = Application(
        job_id=job.id,
        student_id=student.id,
        match_score=match_res["match_score"],
        match_breakdown_json=match_res,
        status="Applied",
        cover_note=req.cover_note
    )
    db.add(app_record)

    # Notify Recruiter
    if job.recruiter and job.recruiter.user_id:
        notification_service.send_notification(
            db=db,
            user_id=job.recruiter.user_id,
            title="New Candidate Application",
            message=f"{current_user.full_name} applied for '{job.title}' with a {match_res['match_score']}% AI match score.",
            notification_type="ApplicationStatus",
            action_url=f"/recruiter/jobs/{job.id}"
        )

    # Notify Student
    notification_service.send_notification(
        db=db,
        user_id=current_user.id,
        title="Application Submitted",
        message=f"Your application for '{job.title}' at {job.company.name} has been successfully submitted.",
        notification_type="ApplicationStatus"
    )

    db.commit()
    db.refresh(app_record)

    return {
        "message": "Application submitted successfully!",
        "application_id": app_record.id,
        "match_score": match_res["match_score"],
        "status": "Applied"
    }

@router.get("/applications")
def get_student_applications(
    current_user: User = Depends(require_role(["STUDENT"])),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found.")

    apps = db.query(Application).filter(Application.student_id == student.id).order_by(Application.applied_at.desc()).all()
    results = []
    for a in apps:
        interview = db.query(a.interviews.property.mapper.class_).filter_by(application_id=a.id).first() if hasattr(a, 'interviews') else None
        results.append({
            "id": a.id,
            "job_id": a.job_id,
            "job_title": a.job.title,
            "company_name": a.job.company.name,
            "company_logo": a.job.company.logo_url,
            "location": a.job.location,
            "match_score": a.match_score,
            "status": a.status,
            "applied_at": a.applied_at.strftime("%d %b %Y"),
            "interview_info": {
                "round": a.interviews[0].round_name,
                "time": a.interviews[0].scheduled_time.strftime("%d %b %Y, %I:%M %p"),
                "mode": a.interviews[0].mode,
                "link": a.interviews[0].meeting_link
            } if a.interviews else None
        })
    return results

@router.post("/projects")
def add_project(
    req: AddProjectRequest,
    current_user: User = Depends(require_role(["STUDENT"])),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    p = Project(
        student_id=student.id,
        title=req.title,
        description=req.description,
        skills_used=req.skills_used,
        repo_url=req.repo_url,
        live_url=req.live_url,
        score_contribution=88.0,
        is_verified=True
    )
    db.add(p)
    db.commit()
    return {"message": "Project added successfully!", "id": p.id}

@router.post("/courses")
def add_course(
    req: AddCourseRequest,
    current_user: User = Depends(require_role(["STUDENT"])),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    c = Course(
        student_id=student.id,
        title=req.title,
        provider=req.provider,
        skills_learned=req.skills_learned,
        completion_date=req.completion_date or "2026",
        score_contribution=90.0,
        is_verified=True
    )
    db.add(c)
    db.commit()
    return {"message": "Course added successfully!", "id": c.id}

@router.post("/certifications")
def add_certification(
    req: AddCertRequest,
    current_user: User = Depends(require_role(["STUDENT"])),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    cert = Certification(
        student_id=student.id,
        name=req.name,
        issuing_org=req.issuing_org,
        issue_date=req.issue_date or "2026",
        credential_id=req.credential_id or "CERT-26044",
        credential_url=req.credential_url,
        score_contribution=92.0,
        is_verified=True
    )
    db.add(cert)
    db.commit()
    return {"message": "Certification added successfully!", "id": cert.id}
