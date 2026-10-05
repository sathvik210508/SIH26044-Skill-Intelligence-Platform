import hashlib
import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import User, Student, StudentSkill, Skill, Department, Institution
from app.ai_engine.proficiency_engine import proficiency_engine

FIRST_NAMES = ["Aarav", "Aditi", "Ananya", "Arjun", "Dev", "Diya", "Ishaan", "Kavya", "Manish", "Neha", "Pranav", "Pooja", "Rahul", "Riya", "Rohan", "Sneha", "Tanvi", "Varun", "Vikas", "Yash", "Aditya", "Meera", "Siddharth", "Shreya", "Kiran"]
LAST_NAMES = ["Sharma", "Verma", "Patel", "Reddy", "Gupta", "Nair", "Iyer", "Kumar", "Singh", "Joshi", "Choudhury", "Bose", "Rao", "Das", "Menon", "Deshmukh", "Kulkarni"]

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class BulkStudentService:
    """
    Service for Institutions/TPOs to batch generate student accounts and profiles
    with realistic academic indicators, curriculum records, and baseline skills.
    """

    def bulk_create_students(
        self,
        db: Session,
        institution_id: int,
        department_name: str,
        current_year: int,
        count: int = 30,
        roll_prefix: str = "24CS"
    ) -> Dict[str, Any]:
        institution = db.query(Institution).filter(Institution.id == institution_id).first()
        if not institution:
            return {"error": "Institution not found"}

        # Find or create department
        dept = db.query(Department).filter(
            Department.institution_id == institution_id,
            Department.name == department_name
        ).first()

        if not dept:
            dept = Department(
                institution_id=institution_id,
                name=department_name,
                code=department_name[:4].upper(),
                student_count=0
            )
            db.add(dept)
            db.flush()

        skills = db.query(Skill).all()
        skill_map = {s.name: s for s in skills}

        created_students = []
        skipped_count = 0
        current_idx = 1

        while len(created_students) < count and current_idx < count + 500:
            roll_number = f"{roll_prefix}{current_idx:03d}"
            email = f"{roll_number.lower()}@{institution.code.lower()}.edu.in"
            current_idx += 1

            # Check duplicate
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                skipped_count += 1
                continue

            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            full_name = f"{first} {last}"
            cgpa = round(random.uniform(6.8, 9.7), 2)

            # Create User
            user = User(
                email=email,
                password_hash=hash_password("Student@123"),
                full_name=full_name,
                role="STUDENT",
                is_active=True
            )
            db.add(user)
            db.flush()

            # Create Student Profile
            student = Student(
                user_id=user.id,
                institution_id=institution_id,
                department_id=dept.id,
                roll_number=roll_number,
                current_year=current_year,
                cgpa=cgpa,
                career_interests=random.choice([
                    "AYUSH Medicine Quality Analyst",
                    "Phytochemical Quality & Safety Specialist",
                    "AYUSH Formulation & Quality Specialist",
                    "AYUSH Pharmacovigilance & Drug Surveillance Officer",
                    "AYUSH Good Manufacturing Practice (GMP) Officer"
                ]),
                placement_status="Seeking Internship/Job"
            )
            db.add(student)
            db.flush()

            # Assign curriculum skills with realistic scores based on current_year
            base_skill_set = ["Ashwagandha", "Triphala", "Clinical Drug Assay & Statistical Evaluation"]
            if current_year >= 3:
                base_skill_set.extend(["Haridra", "Phytochemical Assay & Analysis", "AYUSH Good Manufacturing Practice (GMP)"])
            if current_year >= 4:
                base_skill_set.extend(["Standardized Drug Packaging & Containment", "Automated AYUSH Formulation Intelligence", "Pharmacovigilance & Drug Safety Monitoring"])

            for s_name in base_skill_set:
                if s_name in skill_map:
                    s_obj = skill_map[s_name]
                    
                    # Year-scaled baseline score
                    base_mean = 55.0 if current_year == 2 else (70.0 if current_year == 3 else 82.0)
                    t_score = round(min(98.0, max(30.0, random.gauss(base_mean, 12.0))), 1)
                    p_score = round(min(98.0, max(30.0, random.gauss(base_mean - 2.0, 10.0))), 1)
                    
                    # Calculate proficiency
                    calc = proficiency_engine.calculate_proficiency(
                        test_score=t_score,
                        practical_score=p_score
                    )

                    st_skill = StudentSkill(
                        student_id=student.id,
                        skill_id=s_obj.id,
                        test_score=t_score,
                        practical_score=p_score,
                        proficiency_score=calc["proficiency_score"],
                        evidence_breakdown=calc,
                        status="Verified",
                        source="Curriculum"
                    )
                    db.add(st_skill)

            created_students.append({
                "student_id": student.id,
                "roll_number": roll_number,
                "name": full_name,
                "email": email,
                "cgpa": cgpa
            })

        dept.student_count = (dept.student_count or 0) + len(created_students)
        db.commit()

        return {
            "institution_id": institution_id,
            "department": department_name,
            "current_year": current_year,
            "created_count": len(created_students),
            "skipped_duplicates": skipped_count,
            "sample_accounts": created_students[:5],
            "default_password": "Student@123"
        }

bulk_student_service = BulkStudentService()
