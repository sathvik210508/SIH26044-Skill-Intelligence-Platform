import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from app.database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # STUDENT, RECRUITER, INSTITUTION, ADMIN
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    recruiter_profile = relationship("Recruiter", back_populates="user", uselist=False, cascade="all, delete-orphan")
    institution_profile = relationship("Institution", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False)
    state = Column(String(100), nullable=False, index=True)
    city = Column(String(100), nullable=False)
    tier = Column(String(20), default="Tier 1")
    accreditation = Column(String(50), default="NAAC A++")
    contact_email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    readiness_score = Column(Float, default=75.0)  # Platform Readiness Score (PRS)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="institution_profile")
    departments = relationship("Department", back_populates="institution", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="institution")
    workshops = relationship("Workshop", back_populates="institution")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False)
    student_count = Column(Integer, default=0)

    institution = relationship("Institution", back_populates="departments")
    students = relationship("Student", back_populates="department")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    roll_number = Column(String(50), index=True, nullable=True)
    current_year = Column(Integer, default=3)  # 1, 2, 3, 4
    cgpa = Column(Float, default=8.2)
    resume_path = Column(String(500), nullable=True)
    resume_text = Column(Text, nullable=True)
    career_interests = Column(String(255), default="Full Stack AI Developer, Data Scientist")
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    placement_status = Column(String(50), default="Seeking Internship/Job")  # Seeking, Interning, Placed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="student_profile")
    institution = relationship("Institution", back_populates="students")
    department = relationship("Department", back_populates="students")
    skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="student", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="student", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="student", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="student", cascade="all, delete-orphan")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="student", cascade="all, delete-orphan")
    workshop_registrations = relationship("WorkshopRegistration", back_populates="student", cascade="all, delete-orphan")
    hackathon_registrations = relationship("HackathonRegistration", back_populates="student", cascade="all, delete-orphan")
    placement_records = relationship("PlacementRecord", back_populates="student", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100), index=True, default="Programming")  # Programming, Data Science, Cloud & DevOps, AI/ML, Cybersecurity, Tools
    description = Column(Text, nullable=True)
    aliases = Column(String(500), nullable=True)  # e.g., "ReactJS, React.js, React Native"
    is_curriculum = Column(Boolean, default=True)
    learning_resources_json = Column(JSON, nullable=True)  # Links to docs, courses, videos, roadmaps

    student_skills = relationship("StudentSkill", back_populates="skill")
    assessment_questions = relationship("AssessmentQuestion", back_populates="skill")
    job_requirements = relationship("JobSkillRequirement", back_populates="skill")


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    
    # Proficiency components (0-100)
    test_score = Column(Float, nullable=True)         # T: Adaptive Assessment Score
    practical_score = Column(Float, nullable=True)    # P: Projects / Labs / Assignments Score
    verified_score = Column(Float, nullable=True)     # V: Verified Experience / Resume / Endorsements
    course_score = Column(Float, nullable=True)       # C: Courses / Certifications Score
    
    proficiency_score = Column(Float, default=0.0)    # S = wT*T + wP*P + wV*V + wC*C
    evidence_breakdown = Column(JSON, nullable=True)   # JSON containing explanation of score
    status = Column(String(50), default="Verified")   # Discovered, Pending Verification, Verified, Mastered
    source = Column(String(50), default="Manual")     # Manual, Resume_Extraction, Curriculum, Assessment
    last_assessed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="skills")
    skill = relationship("Skill", back_populates="student_skills")
    evidences = relationship("SkillEvidence", back_populates="student_skill", cascade="all, delete-orphan")


class SkillEvidence(Base):
    __tablename__ = "skill_evidences"

    id = Column(Integer, primary_key=True, index=True)
    student_skill_id = Column(Integer, ForeignKey("student_skills.id"), nullable=False)
    evidence_type = Column(String(50), nullable=False)  # Project, Course, Certification, Resume, Lab
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    score_contribution = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student_skill = relationship("StudentSkill", back_populates="evidences")


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    options_json = Column(JSON, nullable=False)  # Array of 4 option strings
    correct_option_index = Column(Integer, nullable=False)  # 0 to 3
    difficulty_level = Column(String(20), default="Medium")  # Easy, Medium, Hard
    explanation = Column(Text, nullable=True)

    skill = relationship("Skill", back_populates="assessment_questions")


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    score = Column(Float, nullable=False)  # 0 to 100
    total_questions = Column(Integer, default=5)
    correct_answers = Column(Integer, default=0)
    passed = Column(Boolean, default=True)
    details_json = Column(JSON, nullable=True)  # Questions asked, answers given, difficulty trajectory
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="assessment_attempts")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    skills_used = Column(String(500), nullable=True)  # Comma-separated or JSON list
    repo_url = Column(String(500), nullable=True)
    live_url = Column(String(500), nullable=True)
    score_contribution = Column(Float, default=85.0)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="projects")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    title = Column(String(255), nullable=False)
    provider = Column(String(100), default="NPTEL / Coursera")
    skills_learned = Column(String(500), nullable=True)
    completion_date = Column(String(50), nullable=True)
    score_contribution = Column(Float, default=85.0)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="courses")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    name = Column(String(255), nullable=False)
    issuing_org = Column(String(100), nullable=False)
    issue_date = Column(String(50), nullable=True)
    credential_id = Column(String(100), nullable=True)
    credential_url = Column(String(500), nullable=True)
    score_contribution = Column(Float, default=90.0)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="certifications")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    industry = Column(String(100), default="Information Technology")
    size = Column(String(50), default="500-1000")
    website = Column(String(255), nullable=True)
    registration_number = Column(String(100), nullable=True)  # CIN / ROC
    state = Column(String(100), default="Karnataka")
    city = Column(String(100), default="Bengaluru")
    logo_url = Column(String(500), nullable=True)
    
    # Multi-signal verification
    verification_status = Column(String(50), default="Verified")  # Verified, Verification Required, Suspicious
    verification_score = Column(Float, default=92.0)              # 0 to 100
    verification_signals_json = Column(JSON, nullable=True)       # Breakdown of signals
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    recruiters = relationship("Recruiter", back_populates="company")
    jobs = relationship("Job", back_populates="company")
    hiring_records = relationship("HiringRecord", back_populates="company")


class Recruiter(Base):
    __tablename__ = "recruiters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    designation = Column(String(100), default="Talent Acquisition Lead")
    department = Column(String(100), default="Engineering Hiring")
    phone = Column(String(50), nullable=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="recruiter_profile")
    company = relationship("Company", back_populates="recruiters")
    jobs = relationship("Job", back_populates="recruiter")
    interviews = relationship("Interview", back_populates="recruiter")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("recruiters.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    job_type = Column(String(50), default="Full-Time")  # Full-Time, Internship, Apprenticeship
    location = Column(String(100), default="Hybrid (Bengaluru)")
    salary_min = Column(Float, nullable=True)  # LPA or stipend in INR
    salary_max = Column(Float, nullable=True)
    stipend = Column(String(100), nullable=True)
    deadline = Column(String(50), nullable=True)
    eligibility_cgpa = Column(Float, default=6.5)
    eligibility_departments = Column(String(255), default="CSE, IT, AI & DS, ECE")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    recruiter = relationship("Recruiter", back_populates="jobs")
    company = relationship("Company", back_populates="jobs")
    skill_requirements = relationship("JobSkillRequirement", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")


class JobSkillRequirement(Base):
    __tablename__ = "job_skill_requirements"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    required_proficiency = Column(Float, default=70.0)  # 0 to 100%
    importance_weight = Column(String(20), default="High")  # Critical (3x), High (2x), Medium (1x)
    is_mandatory = Column(Boolean, default=True)

    job = relationship("Job", back_populates="skill_requirements")
    skill = relationship("Skill", back_populates="job_requirements")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    match_score = Column(Float, default=0.0)  # Calculated match score (0-100)
    match_breakdown_json = Column(JSON, nullable=True)  # Explainable breakdown
    status = Column(String(50), default="Applied")  # Applied, Shortlisted, Interview, Selected, Rejected
    cover_note = Column(Text, nullable=True)
    applied_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    job = relationship("Job", back_populates="applications")
    student = relationship("Student", back_populates="applications")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    recruiter_id = Column(Integer, ForeignKey("recruiters.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    round_name = Column(String(100), default="Technical Round 1")
    scheduled_time = Column(DateTime, nullable=False)
    mode = Column(String(50), default="Virtual / Google Meet")
    meeting_link = Column(String(500), nullable=True)
    status = Column(String(50), default="Scheduled")  # Scheduled, Completed, Cancelled
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    application = relationship("Application", back_populates="interviews")
    recruiter = relationship("Recruiter", back_populates="interviews")


class Workshop(Base):
    __tablename__ = "workshops"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_skill_name = Column(String(100), nullable=False)
    target_department = Column(String(100), default="All Departments")
    target_year = Column(Integer, default=2)  # 2nd year, 3rd year, etc.
    target_proficiency_max = Column(Float, default=50.0)  # Targeted at students with skill < 50%
    duration_hours = Column(Integer, default=24)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    pre_avg_score = Column(Float, default=38.5)
    post_avg_score = Column(Float, default=64.2)  # +25.7% improvement
    status = Column(String(50), default="Upcoming")  # Upcoming, Ongoing, Completed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    institution = relationship("Institution", back_populates="workshops")
    registrations = relationship("WorkshopRegistration", back_populates="workshop", cascade="all, delete-orphan")


class WorkshopRegistration(Base):
    __tablename__ = "workshop_registrations"

    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    pre_score = Column(Float, nullable=True)
    post_score = Column(Float, nullable=True)
    attended = Column(Boolean, default=True)
    completed = Column(Boolean, default=True)
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)

    workshop = relationship("Workshop", back_populates="registrations")
    student = relationship("Student", back_populates="workshop_registrations")


class Hackathon(Base):
    __tablename__ = "hackathons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    organizer = Column(String(255), default="Ministry / National Skill Council")
    theme = Column(String(255), default="AI & Smart Automation")
    problem_statements_json = Column(JSON, nullable=True)
    eligibility = Column(String(255), default="All Undergraduate & Diploma Students")
    registration_deadline = Column(String(50), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    prizes = Column(String(255), default="₹1,00,000 + Internship Fast-Track")
    is_national = Column(Boolean, default=True)
    status = Column(String(50), default="Active")  # Active, Upcoming, Completed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    registrations = relationship("HackathonRegistration", back_populates="hackathon", cascade="all, delete-orphan")


class HackathonRegistration(Base):
    __tablename__ = "hackathon_registrations"

    id = Column(Integer, primary_key=True, index=True)
    hackathon_id = Column(Integer, ForeignKey("hackathons.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    team_name = Column(String(100), default="Hexagon Innovators")
    project_title = Column(String(255), nullable=True)
    submission_url = Column(String(500), nullable=True)
    status = Column(String(50), default="Registered")  # Registered, Shortlisted, Finalist, Winner
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)

    hackathon = relationship("Hackathon", back_populates="registrations")
    student = relationship("Student", back_populates="hackathon_registrations")


class PlacementRecord(Base):
    __tablename__ = "placement_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    company_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    offer_type = Column(String(50), default="Full-Time")  # Full-Time, Internship, PPO
    package_lpa = Column(Float, default=9.5)
    department = Column(String(100), default="Dravyaguna Vijnana (Herbal Pharmacology)")
    academic_year = Column(String(50), default="2025-2026")
    placed_date = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="placement_records")


class HiringRecord(Base):
    __tablename__ = "hiring_records"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    year = Column(Integer, default=2026)
    full_time_hires = Column(Integer, default=185)
    intern_hires = Column(Integer, default=420)
    total_applications = Column(Integer, default=3820)
    total_shortlisted = Column(Integer, default=640)
    total_selected = Column(Integer, default=185)
    top_departments = Column(String(255), default="Dravyaguna, Rasa Shastra, Quality Control")
    top_skills_demanded = Column(String(255), default="Ashwagandha, Triphala, AYUSH Good Manufacturing Practice (GMP), Automated AYUSH Formulation Intelligence")

    company = relationship("Company", back_populates="hiring_records")


class IndustrySkillDemand(Base):
    __tablename__ = "industry_skill_demands"

    id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(100), unique=True, index=True, nullable=False)
    demand_score = Column(Float, default=85.0)   # % Industry demand
    supply_score = Column(Float, default=60.0)   # % Student supply
    gap_score = Column(Float, default=25.0)      # Demand - Supply
    growth_trend = Column(String(20), default="Rising")  # Rising, Explosive, Stable, Declining
    future_priority = Column(String(50), default="High Priority")  # Critical, High, Moderate
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class GovernmentOpportunity(Base):
    __tablename__ = "government_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    agency = Column(String(255), default="Ministry of AYUSH / CCRAS")
    opportunity_type = Column(String(50), default="Government Internship")  # Internship, Apprenticeship, Fellowship, Skill Scheme
    department = Column(String(100), default="National AYUSH Quality Scheme")
    location = Column(String(100), default="All India / State Centers")
    stipend_or_pay = Column(String(100), default="₹12,000 / month + Certificate")
    eligibility = Column(String(255), default="BAMS / B.Pharm (AYUSH) / M.Sc All Years")
    skills_json = Column(JSON, nullable=True)  # List of relevant skills
    application_url = Column(String(500), default="https://ayush.gov.in")
    deadline = Column(String(50), default="30 Oct 2026")
    is_active = Column(Boolean, default=True)
    is_demo_source = Column(Boolean, default=True)  # Clearly labels demo aggregation layer
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="Info")  # JobMatch, ApplicationStatus, InterviewInvite, Workshop, Hackathon, GovOpp, System
    action_url = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class PlatformSetting(Base):
    __tablename__ = "platform_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value_json = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
