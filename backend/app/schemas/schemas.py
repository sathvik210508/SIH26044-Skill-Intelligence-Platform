from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
import datetime

# --- Auth Schemas ---
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str  # STUDENT, RECRUITER, INSTITUTION, ADMIN
    institution_id: Optional[int] = None
    company_name: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    full_name: str
    email: str
    role: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool

# --- Student Schemas ---
class AddSkillRequest(BaseModel):
    skill_name: str
    evidence_type: Optional[str] = "Practical"  # Test, Practical, Verified, Course
    score: Optional[float] = 80.0
    description: Optional[str] = None
    url: Optional[str] = None

class VerifyExtractedSkillRequest(BaseModel):
    skills: List[Dict[str, Any]]  # [{"skill_name": "Ashwagandha", "verified": True, "self_rating": 80.0}]

class AddProjectRequest(BaseModel):
    title: str
    description: str
    skills_used: str
    repo_url: Optional[str] = None
    live_url: Optional[str] = None

class AddCourseRequest(BaseModel):
    title: str
    provider: str
    skills_learned: str
    completion_date: Optional[str] = None
    certificate_url: Optional[str] = None

class AddCertRequest(BaseModel):
    name: str
    issuing_org: str
    issue_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None

class ApplyJobRequest(BaseModel):
    job_id: int
    cover_note: Optional[str] = None

# --- Assessment Schemas ---
class SubmitQuizRequest(BaseModel):
    skill_id: int
    student_answers: Dict[str, int]
    answers_key: Dict[str, Dict[str, Any]]

# --- Recruiter & Job Schemas ---
class JobSkillReqItem(BaseModel):
    skill_name: str
    required_proficiency: float = 70.0
    importance_weight: str = "High"  # Critical, High, Medium
    is_mandatory: bool = True

class CreateJobRequest(BaseModel):
    title: str
    description: str
    job_type: str = "Full-Time"  # Full-Time, Internship, Apprenticeship
    location: str = "Hybrid (Bengaluru)"
    salary_min: Optional[float] = 8.0
    salary_max: Optional[float] = 14.0
    stipend: Optional[str] = None
    deadline: Optional[str] = "30 Nov 2026"
    eligibility_cgpa: float = 6.5
    eligibility_departments: str = "Dravyaguna, Rasa Shastra, Quality Control"
    skills_matrix: List[JobSkillReqItem]

class UpdateApplicationStatusRequest(BaseModel):
    status: str  # Applied, Shortlisted, Interview, Selected, Rejected
    feedback: Optional[str] = None

class ScheduleInterviewRequest(BaseModel):
    application_id: int
    scheduled_time: str
    mode: str = "Virtual / Google Meet"
    meeting_link: Optional[str] = "https://meet.google.com/sih-26044-interview"
    round_name: str = "Technical Round 1"

# --- Institution Schemas ---
class BulkCreateStudentsRequest(BaseModel):
    department_name: str = "Dravyaguna Vijnana (Herbal Pharmacology)"
    current_year: int = 2
    count: int = 30
    roll_prefix: str = "24NIA"

class CreateWorkshopRequest(BaseModel):
    title: str
    description: str
    target_skill_name: str
    target_department: str = "Dravyaguna Vijnana (Herbal Pharmacology)"
    target_year: int = 2
    target_proficiency_max: float = 50.0
    duration_hours: int = 24
    start_date: Optional[str] = "15 Oct 2026"
    end_date: Optional[str] = "30 Oct 2026"

# --- Admin Schemas ---
class CreateHackathonRequest(BaseModel):
    title: str
    theme: str
    problem_statements: List[str]
    eligibility: str = "All AYUSH, BAMS & Pharmacy Students"
    prizes: str = "₹1,50,000 + Internship Fast-Track"
    registration_deadline: str = "15 Nov 2026"
    start_date: str = "20 Nov 2026"
    end_date: str = "22 Nov 2026"

class CreateGovOpportunityRequest(BaseModel):
    title: str
    agency: str = "Ministry of AYUSH / CCRAS"
    opportunity_type: str = "Government Internship"
    department: str = "National AYUSH Quality Scheme"
    location: str = "Pan-India"
    stipend_or_pay: str = "₹15,000 / month"
    eligibility: str = "BAMS / B.Pharm (AYUSH) All Years"
    skills: List[str] = ["Ashwagandha", "Triphala", "AYUSH Good Manufacturing Practice (GMP)"]
    application_url: str = "https://ayush.gov.in"
    deadline: str = "31 Dec 2026"

class UpdateCompanyVerifyRequest(BaseModel):
    company_id: int
    verification_status: str  # Verified, Verification Required, Suspicious
    notes: Optional[str] = None

# --- AI Assistant Schemas ---
class AssistantQueryRequest(BaseModel):
    query: str
    active_tab: Optional[str] = None

class ConfirmActionRequest(BaseModel):
    action_type: str
    parameters: Dict[str, Any]
