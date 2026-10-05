from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.models import User, Student, Recruiter, Institution, Company, Department
from app.schemas.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.auth.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    role = req.role.upper()
    if role not in ["STUDENT", "RECRUITER", "INSTITUTION", "ADMIN"]:
        raise HTTPException(status_code=400, detail="Invalid role specified.")

    user = User(
        email=req.email.lower().strip(),
        password_hash=hash_password(req.password),
        full_name=req.full_name.strip(),
        role=role,
        is_active=True
    )
    db.add(user)
    db.flush()

    if role == "STUDENT":
        inst_id = req.institution_id or 1
        dept = db.query(Department).filter(Department.institution_id == inst_id).first()
        dept_id = dept.id if dept else None
        student = Student(
            user_id=user.id,
            institution_id=inst_id,
            department_id=dept_id,
            roll_number=f"24ST{user.id:03d}",
            current_year=3,
            cgpa=8.4,
            career_interests="Full Stack AI Developer, Data Scientist"
        )
        db.add(student)
    elif role == "RECRUITER":
        company = None
        if req.company_name:
            company = db.query(Company).filter(Company.name == req.company_name).first()
        if not company:
            company = db.query(Company).first()
        
        company_id = company.id if company else 1
        recruiter = Recruiter(
            user_id=user.id,
            company_id=company_id,
            designation="Talent Acquisition Lead",
            department="Engineering Hiring"
        )
        db.add(recruiter)
    elif role == "INSTITUTION":
        inst = Institution(
            user_id=user.id,
            name=f"{req.full_name} Institute of Technology",
            code=f"IIT{user.id:02d}",
            state="Maharashtra",
            city="Mumbai",
            tier="Tier 1",
            accreditation="NAAC A++"
        )
        db.add(inst)

    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role, "email": user.email})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role
    )

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token({"sub": str(user.id), "role": user.role, "email": user.email})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role
    )

@router.post("/demo-login/{role}", response_model=TokenResponse)
def demo_login(role: str, db: Session = Depends(get_db)):
    r = role.upper()
    user = db.query(User).filter(User.role == r).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"No seeded demo user found for role {role}")

    token = create_access_token({"sub": str(user.id), "role": user.role, "email": user.email})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active
    )
