import hashlib
import datetime
import random
from sqlalchemy.orm import Session
from app.database.db import Base, engine, SessionLocal
from app.models.models import (
    User, Student, Recruiter, Institution, Department, Skill, StudentSkill, SkillEvidence,
    AssessmentQuestion, Project, Course, Certification, Company, Job, JobSkillRequirement,
    Application, Interview, Workshop, WorkshopRegistration, Hackathon, HackathonRegistration,
    PlacementRecord, HiringRecord, IndustrySkillDemand, GovernmentOpportunity, Notification, PlatformSetting
)
from app.ai_engine.proficiency_engine import proficiency_engine
from app.ai_engine.matching_engine import matching_engine

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

SKILLS_CATALOG = [
    {"name": "Ashwagandha", "category": "Generic AYUSH Medicines", "aliases": "withania somnifera, indian ginseng, asgandh, ashwagandha churna, python, py", "desc": "Premier adaptogenic Rasayana herb promoting vitality, stress resilience, and neuromuscular health"},
    {"name": "Triphala", "category": "Classical Formulations", "aliases": "triphala churna, three fruits, amalaki bibhitaki haritaki, sql, mysql, postgresql", "desc": "Classical tridoshic formulation of three fruits for gastrointestinal balance, gentle cleansing, and metabolic support"},
    {"name": "Phytochemical Assay & Analysis", "category": "Quality Control & Standardization", "aliases": "phytochemical assay, phytochemical analysis, bio-assay, quantitative assay, ml, machine learning", "desc": "Quantitative phytochemical assays, active biomarker quantification, and analytical profiling"},
    {"name": "HPLC Standardization & Fingerprinting", "category": "Quality Control & Standardization", "aliases": "hplc, hptlc, chromatographic fingerprinting, deep learning, dl", "desc": "High-Performance Liquid Chromatography and HPTLC fingerprinting for herbal drug authentication"},
    {"name": "Haridra / Curcumin", "category": "Generic AYUSH Medicines", "aliases": "haridra, turmeric, curcuma longa, haldi, curcuminoids, react, reactjs", "desc": "Curcuma longa standardization, curcuminoid quantification, and anti-inflammatory formulation protocols"},
    {"name": "Turmeric", "category": "Generic AYUSH Medicines", "aliases": "curcumin, haridra, haldi, curcuma longa, javascript, js", "desc": "Potent anti-inflammatory and antioxidant herb widely used for systemic wellness and wound healing"},
    {"name": "Tulsi", "category": "Generic AYUSH Medicines", "aliases": "holy basil, ocimum sanctum, tulasi, typescript, ts", "desc": "Sacred adaptogenic herb supporting respiratory health, immunity, and mental clarity"},
    {"name": "Guduchi / Giloy", "category": "Generic AYUSH Medicines", "aliases": "guduchi, tinospora cordifolia, giloy, amrita, c++, cpp", "desc": "Immuno-modulator and antipyretic bitter tonic known as heavenly nectar (Amrita)"},
    {"name": "Brahmi", "category": "Generic AYUSH Medicines", "aliases": "bacopa monnieri, jalbrahmi, medhya rasayana, java, core java", "desc": "Premier Medhya Rasayana herb enhancing memory, cognition, intellect, and calming the nervous system"},
    {"name": "Ayurvedic Pharmacopoeia Protocols (API)", "category": "Regulatory & Standards", "aliases": "api protocols, ayurvedic pharmacopoeia of india, pharmacopoeial standards, fastapi, fast api", "desc": "Official Ayurvedic Pharmacopoeia of India (API) regulatory monographs, parameters, and testing limits"},
    {"name": "AYUSH Good Manufacturing Practice (GMP)", "category": "Pharmaceutical Operations", "aliases": "ayush gmp, gmp compliance, schedule t, who gmp, cloud computing, cloud", "desc": "Schedule T Good Manufacturing Practices, sterile processing, sanitation, and regulatory plant compliance"},
    {"name": "Batch Quality Assurance (QA)", "category": "Quality Assurance", "aliases": "batch qa, quality assurance, in-process quality control, ipqc, aws", "desc": "Standardized batch release testing, quality assurance audits, and analytical monograph compliance"},
    {"name": "Standardized Drug Packaging & Containment", "category": "Packaging & Containment", "aliases": "packaging standards, pharmaceutical containment, stability packaging, tamper evident, docker", "desc": "Container closure integrity, light-resistant packaging, moisture protection, and shelf-life preservation"},
    {"name": "Ayurvedic Pharmaceutical Batch Processing", "category": "Pharmaceutical Processing", "aliases": "batch processing, pharmaceutical manufacturing, bmr processing, kubernetes, k8s", "desc": "Scaled manufacturing protocols for classical Asava, Arishta, Avaleha, and Bhasma preparations"},
    {"name": "Pharmacovigilance & Drug Safety Monitoring", "category": "Drug Safety & Vigilance", "aliases": "pharmacovigilance, drug safety, adverse drug reaction monitoring, adr, cybersecurity", "desc": "National AYUSH Pharmacovigilance Program, adverse event documentation, and heavy metal safety monitoring"},
    {"name": "AYUSH Market Analytics & Consumption Trends", "category": "Market & Supply Intelligence", "aliases": "market analytics, ayush consumption trends, supply trends, power bi, powerbi", "desc": "National herbal raw material demand analytics, seasonal pricing trends, and market intelligence"},
    {"name": "Batch Manufacturing Records (BMR)", "category": "Documentation & Quality", "aliases": "bmr, batch records, manufacturing documentation, excel, ms excel", "desc": "Schedule T compliant Batch Manufacturing Records, reconciliation logs, and inspection documentation"},
    {"name": "Clinical Drug Assay & Statistical Evaluation", "category": "Clinical & Statistical Evaluation", "aliases": "clinical assay, statistical drug evaluation, bio-statistical assay, data analysis", "desc": "Empirical evaluation of clinical trial endpoints, safety biomarkers, and therapeutic efficacy indices"},
    {"name": "Automated AYUSH Formulation Intelligence", "category": "Formulation Science & Informatics", "aliases": "formulation intelligence, automated monograph query, genai, generative ai", "desc": "AI-assisted classical monograph interpretation, drug-herb interaction forecasting, and formulation design"},
    {"name": "Classical Ayurvedic Monograph Informatics", "category": "Formulation Science & Informatics", "aliases": "monograph informatics, classical text parsing, samhita query, nlp", "desc": "Lexical extraction and taxonomy mapping from Charaka, Sushruta, and Ashtanga Hridaya texts"},
    {"name": "Herbal Raw Material Botanical Inspection", "category": "Botanical Quality & Identification", "aliases": "botanical inspection, macroscopic inspection, adulterant detection, computer vision, cv", "desc": "Macroscopic and microscopic authentication of medicinal plants and automated detection of adulterants"},
    {"name": "AYUSH Monograph & Batch Record Versioning", "category": "Regulatory Documentation", "aliases": "monograph versioning, audit trail, batch record revision, git, github", "desc": "Audit-trail compliant revision management and version control for master formulation dossiers"}
]

INDUSTRY_DEMANDS_SEED = [
    {"skill_name": "Ashwagandha", "demand_score": 91.0, "supply_score": 78.0, "growth_trend": "Rising", "future_priority": "Critical"},
    {"skill_name": "Triphala", "demand_score": 88.0, "supply_score": 71.0, "growth_trend": "Stable", "future_priority": "High Priority"},
    {"skill_name": "Phytochemical Assay & Analysis", "demand_score": 82.0, "supply_score": 54.0, "growth_trend": "Rising", "future_priority": "Critical"},
    {"skill_name": "AYUSH Good Manufacturing Practice (GMP)", "demand_score": 76.0, "supply_score": 39.0, "growth_trend": "Explosive", "future_priority": "Critical"},
    {"skill_name": "Standardized Drug Packaging & Containment", "demand_score": 68.0, "supply_score": 28.0, "growth_trend": "Explosive", "future_priority": "Critical"},
    {"skill_name": "Automated AYUSH Formulation Intelligence", "demand_score": 85.0, "supply_score": 24.0, "growth_trend": "Explosive", "future_priority": "Critical"},
    {"skill_name": "Haridra / Curcumin", "demand_score": 80.0, "supply_score": 68.0, "growth_trend": "Rising", "future_priority": "High Priority"},
    {"skill_name": "AYUSH Market Analytics & Consumption Trends", "demand_score": 74.0, "supply_score": 45.0, "growth_trend": "Rising", "future_priority": "High Priority"},
    {"skill_name": "Pharmacovigilance & Drug Safety Monitoring", "demand_score": 72.0, "supply_score": 34.0, "growth_trend": "Rising", "future_priority": "High Priority"}
]

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).first():
            print("Database already contains data. Skipping initial seeding.")
            return

        print("Seeding database with realistic SIH26044 demo data...")

        # 1. Platform Settings
        db.add(PlatformSetting(
            key="proficiency_weights",
            value_json={"test": 0.40, "practical": 0.30, "verified": 0.15, "course": 0.15},
            description="Default weights for skill proficiency calculation S = wT*T + wP*P + wV*V + wC*C"
        ))

        # 2. Master Skills
        skill_objs = {}
        for s in SKILLS_CATALOG:
            obj = Skill(
                name=s["name"],
                category=s["category"],
                aliases=s["aliases"],
                description=s["desc"],
                is_curriculum=True
            )
            db.add(obj)
            db.flush()
            skill_objs[s["name"]] = obj

        # 3. Industry Demands
        for d in INDUSTRY_DEMANDS_SEED:
            db.add(IndustrySkillDemand(
                skill_name=d["skill_name"],
                demand_score=d["demand_score"],
                supply_score=d["supply_score"],
                gap_score=round(d["demand_score"] - d["supply_score"], 1),
                growth_trend=d["growth_trend"],
                future_priority=d["future_priority"]
            ))

        # 4. Institutions
        inst_data = [
            {"name": "National Institute of Ayurveda (NIA Jaipur)", "code": "NIA", "state": "Rajasthan", "city": "Jaipur", "tier": "Tier 1", "score": 88.5},
            {"name": "All India Institute of Ayurveda (AIIA New Delhi)", "code": "AIIA", "state": "Delhi NCR", "city": "New Delhi", "tier": "Tier 1", "score": 84.0},
            {"name": "Institute of Teaching & Research in Ayurveda (ITRA Jamnagar)", "code": "ITRA", "state": "Gujarat", "city": "Jamnagar", "tier": "Tier 1", "score": 79.5},
            {"name": "Faculty of Ayurveda, Banaras Hindu University (BHU)", "code": "BHU", "state": "Uttar Pradesh", "city": "Varanasi", "tier": "Tier 1", "score": 82.0}
        ]

        institutions = []
        for idata in inst_data:
            inst = Institution(
                name=idata["name"],
                code=idata["code"],
                state=idata["state"],
                city=idata["city"],
                tier=idata["tier"],
                readiness_score=idata["score"],
                website=f"https://www.{idata['code'].lower()}.edu.in"
            )
            db.add(inst)
            db.flush()
            institutions.append(inst)

            # Add Departments
            for dname, dcode in [("Dravyaguna Vijnana (Herbal Pharmacology)", "DV"), ("Rasa Shastra & Bhaishajya Kalpana (Pharmaceutical Processing)", "RSBK"), ("Ayurvedic Quality Control & Drug Standardization", "AQCDS"), ("Agada Tantra & Pharmacovigilance", "ATP")]:
                dept = Department(institution_id=inst.id, name=dname, code=dcode, student_count=120)
                db.add(dept)

        db.flush()
        primary_inst = institutions[0]
        primary_depts = db.query(Department).filter(Department.institution_id == primary_inst.id).all()

        # 5. Companies
        company_data = [
            {"name": "Dabur AYUSH Life Sciences", "industry": "Ayurvedic Pharmaceuticals & Classical Formulations", "size": "1000-5000", "website": "https://dabur.com", "reg": "CIN-L24230DL1975PLC007908", "state": "Delhi NCR", "city": "New Delhi", "status": "Verified", "score": 96.0},
            {"name": "Himalaya Herbal Healthcare", "industry": "Herbal Therapeutics & Standardization", "size": "500-1000", "website": "https://himalayawellness.in", "reg": "CIN-U24231KA1930PTC001234", "state": "Karnataka", "city": "Bengaluru", "status": "Verified", "score": 92.0},
            {"name": "Patanjali Bio-Research Institute", "industry": "Ayurvedic Phytochemistry & Generic Formulations", "size": "2000+", "website": "https://patanjaliayurved.org", "reg": "CIN-U24233UR2006PLC031405", "state": "Uttarakhand", "city": "Haridwar", "status": "Verified", "score": 94.0},
            {"name": "Charak Pharma Laboratories", "industry": "Standardized Herbal Formulations & Quality", "size": "100-500", "website": "https://charak.com", "reg": "CIN-U24239MH1947PTC005892", "state": "Maharashtra", "city": "Mumbai", "status": "Verified", "score": 88.0},
            {"name": "Baidyanath Pharmaceuticals", "industry": "Classical Ayurvedic Medicines & Bhasmas", "size": "200-500", "website": "https://baidyanath.co.in", "reg": "CIN-U24230WB1917PLC002765", "state": "West Bengal", "city": "Kolkata", "status": "Verified", "score": 89.0},
            {"name": "Zandu Healthcare", "industry": "Ayurvedic Wellness & Phytopharmaceuticals", "size": "50-200", "website": "https://zanducare.com", "reg": "CIN-L24230MH1910PLC000312", "state": "Gujarat", "city": "Vapi", "status": "Verification Required", "score": 68.0}
        ]

        companies = []
        for cdata in company_data:
            c = Company(
                name=cdata["name"],
                industry=cdata["industry"],
                size=cdata["size"],
                website=cdata["website"],
                registration_number=cdata["reg"],
                state=cdata["state"],
                city=cdata["city"],
                verification_status=cdata["status"],
                verification_score=cdata["score"]
            )
            db.add(c)
            db.flush()
            companies.append(c)

            # Add Hiring Records for analytics
            db.add(HiringRecord(
                company_id=c.id,
                year=2026,
                full_time_hires=random.randint(60, 200),
                intern_hires=random.randint(150, 450),
                total_applications=random.randint(1800, 4200),
                total_shortlisted=random.randint(300, 700),
                total_selected=random.randint(60, 200)
            ))

        # 6. Core Demo Users
        # User 1: Student (Rahul Sharma)
        u_student = User(
            email="student@sih.gov.in",
            password_hash=hash_pw("Student@123"),
            full_name="Rahul Sharma",
            role="STUDENT"
        )
        db.add(u_student)
        db.flush()

        st_profile = Student(
            user_id=u_student.id,
            institution_id=primary_inst.id,
            department_id=primary_depts[0].id,
            roll_number="23NIA042",
            current_year=3,
            cgpa=8.95,
            career_interests="AYUSH Medicine Quality Analyst, Pharmaceutical Quality Specialist",
            bio="Pre-final year Dravyaguna & Pharmaceutical Sciences scholar passionate about Phytochemical Standardization, Classical Ayurvedic Formulations, and AYUSH GMP Compliance.",
            placement_status="Seeking Internship/Job"
        )
        db.add(st_profile)
        db.flush()

        # Seed Rahul's Skills with real T/P/V/C scores
        student_skill_presets = [
            {"skill": "Ashwagandha", "T": 88.0, "P": 82.0, "V": 80.0, "C": 90.0},
            {"skill": "Triphala", "T": 84.0, "P": 78.0, "V": 85.0, "C": 75.0},
            {"skill": "Phytochemical Assay & Analysis", "T": 80.0, "P": 85.0, "V": 75.0, "C": 80.0},
            {"skill": "Haridra / Curcumin", "T": 75.0, "P": 80.0, "V": 70.0, "C": None},  # Missing C test
            {"skill": "Ayurvedic Pharmacopoeia Protocols (API)", "T": 85.0, "P": 90.0, "V": None, "C": None},
            {"skill": "Clinical Drug Assay & Statistical Evaluation", "T": 82.0, "P": 80.0, "V": 75.0, "C": 88.0},
            {"skill": "Standardized Drug Packaging & Containment", "T": 45.0, "P": 40.0, "V": None, "C": None},  # Gap skill
            {"skill": "AYUSH Good Manufacturing Practice (GMP)", "T": 38.0, "P": 42.0, "V": None, "C": None}  # Gap skill
        ]

        for sp in student_skill_presets:
            s_obj = skill_objs.get(sp["skill"])
            if s_obj:
                calc = proficiency_engine.calculate_proficiency(
                    test_score=sp["T"],
                    practical_score=sp["P"],
                    verified_score=sp["V"],
                    course_score=sp["C"]
                )
                st_sk = StudentSkill(
                    student_id=st_profile.id,
                    skill_id=s_obj.id,
                    test_score=sp["T"],
                    practical_score=sp["P"],
                    verified_score=sp["V"],
                    course_score=sp["C"],
                    proficiency_score=calc["proficiency_score"],
                    evidence_breakdown=calc,
                    status="Verified",
                    source="Curriculum"
                )
                db.add(st_sk)
                db.flush()

                # Add Evidence
                db.add(SkillEvidence(
                    student_skill_id=st_sk.id,
                    evidence_type="Project",
                    title=f"Hands-on Implementation in {sp['skill']}",
                    score_contribution=sp["P"],
                    is_verified=True
                ))

        # Rahul's Projects
        db.add(Project(
            student_id=st_profile.id,
            title="Automated AYUSH Medicine Quality & Monograph Registry",
            description="Built standardized monograph testing platform with Ayurvedic Pharmacopoeia Protocols, Phytochemical Assays, and Assay testing.",
            skills_used="Ashwagandha, Ayurvedic Pharmacopoeia Protocols (API), Phytochemical Assay & Analysis",
            repo_url="https://ayush.gov.in/monographs/withania-somnifera",
            live_url="https://ayushportal.nic.in/quality-registry"
        ))
        db.add(Project(
            student_id=st_profile.id,
            title="Standardized Triphala Classical Formulation Pipeline",
            description="High-throughput quality testing pipeline validating ratio balancing across Haritaki, Bibhitaki, and Amalaki batches.",
            skills_used="Ashwagandha, Triphala, Haridra / Curcumin, Standardized Drug Packaging & Containment",
            repo_url="https://ayush.gov.in/monographs/triphala-churna"
        ))

        # Rahul's Courses & Certifications
        db.add(Course(
            student_id=st_profile.id,
            title="Classical Phytochemical Standardization & Assay Certification",
            provider="National Medicinal Plants Board / CCRAS",
            skills_learned="Phytochemical Assay & Analysis, Ashwagandha, HPLC Standardization & Fingerprinting",
            completion_date="May 2025"
        ))
        db.add(Certification(
            student_id=st_profile.id,
            name="WHO-AYUSH Good Manufacturing Practice (GMP) Certified Quality Officer",
            issuing_org="Ministry of AYUSH Pharmacopoeia Commission",
            issue_date="Aug 2025",
            credential_id="AYUSH-GMP-2025-99882",
            credential_url="https://ayush.gov.in/verification"
        ))

        # User 2: Recruiter (Priya Menon - Dabur AYUSH Life Sciences)
        u_recruiter = User(
            email="recruiter@dabur.com",
            password_hash=hash_pw("Recruiter@123"),
            full_name="Priya Menon",
            role="RECRUITER"
        )
        db.add(u_recruiter)
        db.flush()

        recruiter_profile = Recruiter(
            user_id=u_recruiter.id,
            company_id=companies[0].id,
            designation="Head of AYUSH Pharmaceutical Quality & Campus Hiring",
            department="Quality Control & Botanical Procurement",
            phone="+91 98765 43210",
            is_verified=True
        )
        db.add(recruiter_profile)
        db.flush()

        # User 3: Institution / TPO (Prof. S. Ranganathan - NIA Jaipur)
        u_inst = User(
            email="tpo@nia.edu.in",
            password_hash=hash_pw("Institution@123"),
            full_name="Prof. S. Ranganathan",
            role="INSTITUTION"
        )
        db.add(u_inst)
        db.flush()
        primary_inst.user_id = u_inst.id

        # User 4: Admin / Ministry (Dr. V. K. Saraswat)
        u_admin = User(
            email="admin@ministry.gov.in",
            password_hash=hash_pw("Admin@123"),
            full_name="Dr. V. K. Saraswat",
            role="ADMIN"
        )
        db.add(u_admin)
        db.flush()

        # 7. Seed 35+ Additional Students across multiple institutions & departments
        first_names = ["Ananya", "Arjun", "Aditi", "Dev", "Diya", "Ishaan", "Kavya", "Manish", "Neha", "Pranav", "Pooja", "Rohan", "Sneha", "Tanvi", "Varun", "Vikas", "Yash", "Meera", "Siddharth", "Shreya", "Kiran", "Nikhil", "Aishwarya", "Vikram", "Gaurav"]
        last_names = ["Patel", "Verma", "Reddy", "Gupta", "Nair", "Iyer", "Kumar", "Singh", "Joshi", "Choudhury", "Bose", "Rao", "Das", "Menon", "Deshmukh"]

        all_students = [st_profile]
        for i in range(1, 35):
            inst = random.choice(institutions)
            depts = db.query(Department).filter(Department.institution_id == inst.id).all()
            dept = random.choice(depts) if depts else primary_depts[0]
            
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            email = f"{fn.lower()}.{ln.lower()}{i}@{inst.code.lower()}.edu.in"
            yr = random.choice([2, 3, 4])
            cgpa = round(random.uniform(7.1, 9.6), 2)

            u = User(
                email=email,
                password_hash=hash_pw("Student@123"),
                full_name=f"{fn} {ln}",
                role="STUDENT"
            )
            db.add(u)
            db.flush()

            st = Student(
                user_id=u.id,
                institution_id=inst.id,
                department_id=dept.id,
                roll_number=f"{inst.code}{yr}DV{i:03d}",
                current_year=yr,
                cgpa=cgpa,
                career_interests=random.choice([
                    "AYUSH Medicine Quality Analyst, Pharmaceutical Quality Specialist",
                    "AYUSH Formulation Specialist, GMP Quality Officer",
                    "Pharmacovigilance & Drug Surveillance Officer, Regulatory Compliance Specialist",
                    "Ayurvedic Phytochemist, Classical Drug Assayer",
                    "AYUSH Market Analyst, Raw Material Procurement Officer"
                ]),
                placement_status=random.choice(["Seeking Internship/Job", "Seeking Internship/Job", "Interning", "Placed"])
            )
            db.add(st)
            db.flush()
            all_students.append(st)

            # Seed 4-6 skills per student
            student_skills_subset = random.sample(list(skill_objs.keys()), random.randint(4, 7))
            for sname in student_skills_subset:
                sobj = skill_objs[sname]
                base_score = 50.0 if yr == 2 else (68.0 if yr == 3 else 82.0)
                t = round(min(98.0, max(30.0, random.gauss(base_score, 12.0))), 1)
                p = round(min(98.0, max(30.0, random.gauss(base_score, 10.0))), 1)
                v = round(min(95.0, max(30.0, random.gauss(base_score, 10.0))), 1) if random.random() > 0.3 else None
                c = round(min(95.0, max(30.0, random.gauss(base_score, 10.0))), 1) if random.random() > 0.4 else None

                calc = proficiency_engine.calculate_proficiency(test_score=t, practical_score=p, verified_score=v, course_score=c)

                st_sk = StudentSkill(
                    student_id=st.id,
                    skill_id=sobj.id,
                    test_score=t,
                    practical_score=p,
                    verified_score=v,
                    course_score=c,
                    proficiency_score=calc["proficiency_score"],
                    evidence_breakdown=calc,
                    status="Verified",
                    source="Curriculum"
                )
                db.add(st_sk)

        db.flush()

        # 8. Seed Jobs with Skill Requirement Matrices
        jobs_seed = [
            {
                "title": "AYUSH Medicine Quality & Phytochemical Analyst (Campus 2026)",
                "company": companies[0], # Dabur AYUSH Life Sciences
                "type": "Full-Time",
                "location": "Bengaluru (Hybrid)",
                "sal_min": 14.0, "sal_max": 22.0, "cgpa": 7.5,
                "matrix": [
                    {"skill": "Ashwagandha", "prof": 80.0, "imp": "Critical"},
                    {"skill": "Phytochemical Assay & Analysis", "prof": 75.0, "imp": "Critical"},
                    {"skill": "HPLC Standardization & Fingerprinting", "prof": 70.0, "imp": "High"},
                    {"skill": "Triphala", "prof": 65.0, "imp": "Medium"}
                ]
            },
            {
                "title": "Ayurvedic Formulation Quality & BMR Specialist",
                "company": companies[2], # Patanjali Bio-Research Institute
                "type": "Full-Time",
                "location": "Gurugram / Hybrid",
                "sal_min": 10.0, "sal_max": 16.0, "cgpa": 7.0,
                "matrix": [
                    {"skill": "Triphala", "prof": 80.0, "imp": "Critical"},
                    {"skill": "Ashwagandha", "prof": 75.0, "imp": "High"},
                    {"skill": "AYUSH Market Analytics & Consumption Trends", "prof": 70.0, "imp": "Critical"},
                    {"skill": "Batch Manufacturing Records (BMR)", "prof": 85.0, "imp": "High"}
                ]
            },
            {
                "title": "AYUSH GMP & Standardized Containment Intern",
                "company": companies[1], # Himalaya Herbal Healthcare
                "type": "Internship",
                "location": "Pune / Remote",
                "stipend": "₹45,000 / month", "cgpa": 6.5,
                "matrix": [
                    {"skill": "AYUSH Good Manufacturing Practice (GMP)", "prof": 75.0, "imp": "Critical"},
                    {"skill": "Standardized Drug Packaging & Containment", "prof": 70.0, "imp": "Critical"},
                    {"skill": "Ayurvedic Pharmaceutical Batch Processing", "prof": 60.0, "imp": "High"},
                    {"skill": "Ashwagandha", "prof": 65.0, "imp": "Medium"}
                ]
            },
            {
                "title": "Senior Formulation Scientist & Assay Specialist",
                "company": companies[0], # Dabur AYUSH Life Sciences
                "type": "Full-Time",
                "location": "Bengaluru",
                "sal_min": 12.0, "sal_max": 18.0, "cgpa": 7.0,
                "matrix": [
                    {"skill": "Haridra / Curcumin", "prof": 80.0, "imp": "Critical"},
                    {"skill": "Turmeric", "prof": 85.0, "imp": "High"},
                    {"skill": "Ayurvedic Pharmacopoeia Protocols (API)", "prof": 75.0, "imp": "High"},
                    {"skill": "Triphala", "prof": 70.0, "imp": "Medium"}
                ]
            },
            {
                "title": "AYUSH Pharmacovigilance & Drug Safety Associate",
                "company": companies[4], # Baidyanath Pharmaceuticals
                "type": "Full-Time",
                "location": "Bengaluru",
                "sal_min": 11.0, "sal_max": 15.5, "cgpa": 7.0,
                "matrix": [
                    {"skill": "Pharmacovigilance & Drug Safety Monitoring", "prof": 80.0, "imp": "Critical"},
                    {"skill": "Ashwagandha", "prof": 70.0, "imp": "High"},
                    {"skill": "AYUSH Good Manufacturing Practice (GMP)", "prof": 65.0, "imp": "Medium"}
                ]
            }
        ]

        jobs = []
        for jdata in jobs_seed:
            job = Job(
                recruiter_id=recruiter_profile.id,
                company_id=jdata["company"].id,
                title=jdata["title"],
                description=f"Join {jdata['company'].name} as a {jdata['title']}. We are looking for talented candidates with proven skills.",
                job_type=jdata["type"],
                location=jdata["location"],
                salary_min=jdata.get("sal_min"),
                salary_max=jdata.get("sal_max"),
                stipend=jdata.get("stipend"),
                deadline="30 Nov 2026",
                eligibility_cgpa=jdata["cgpa"],
                eligibility_departments="Dravyaguna Vijnana, Rasa Shastra, Ayurvedic Quality Control, Agada Tantra",
                is_active=True,
                is_verified=True
            )
            db.add(job)
            db.flush()
            jobs.append(job)

            # Add Job Skill Requirements
            for m in jdata["matrix"]:
                sk_obj = skill_objs.get(m["skill"])
                if sk_obj:
                    db.add(JobSkillRequirement(
                        job_id=job.id,
                        skill_id=sk_obj.id,
                        required_proficiency=m["prof"],
                        importance_weight=m["imp"],
                        is_mandatory=True
                    ))

        db.flush()

        # 9. Seed Realistic Applications and Pipeline Stages
        # Let's create applications for Rahul and other students
        primary_job = jobs[0] # AYUSH Medicine Quality & Phytochemical Analyst
        for idx, student in enumerate(all_students[:18]):
            st_skills = {s.skill.name.lower(): s.proficiency_score for s in student.skills}
            reqs = [{"skill_name": r.skill.name, "required_proficiency": r.required_proficiency, "importance_weight": r.importance_weight} for r in primary_job.skill_requirements]
            
            match_res = matching_engine.calculate_match(
                student_skills=st_skills,
                job_requirements=reqs,
                student_cgpa=student.cgpa,
                required_cgpa=primary_job.eligibility_cgpa
            )

            # Assign realistic pipeline statuses
            status = "Applied"
            if idx == 0: # Rahul Sharma
                status = "Interview"
            elif idx in [1, 2, 3]:
                status = "Shortlisted"
            elif idx == 4:
                status = "Selected"
            elif idx > 12:
                status = "Rejected"

            app = Application(
                job_id=primary_job.id,
                student_id=student.id,
                match_score=match_res["match_score"],
                match_breakdown_json=match_res,
                status=status,
                cover_note="Excited to apply my Ayurvedic pharmaceutical expertise, classical monograph knowledge, and quality control background to high-impact AYUSH medicine challenges."
            )
            db.add(app)
            db.flush()

            if status == "Interview":
                db.add(Interview(
                    application_id=app.id,
                    recruiter_id=recruiter_profile.id,
                    student_id=student.id,
                    round_name="Technical Round 1: Classical Monograph Analysis & Phytochemical Quality Standards",
                    scheduled_time=datetime.datetime.utcnow() + datetime.timedelta(days=2),
                    mode="Virtual / Google Meet",
                    meeting_link="https://meet.google.com/sih-26044-interview",
                    status="Scheduled"
                ))

        # 10. Seed Workshops with Pre & Post Training Scores
        workshops_seed = [
            {"title": "AYUSH Good Manufacturing Practice (GMP) & Plant Audit Masterclass", "skill": "AYUSH Good Manufacturing Practice (GMP)", "dept": "Dravyaguna Vijnana (Herbal Pharmacology)", "yr": 2, "pre": 38.5, "post": 66.0, "status": "Completed"},
            {"title": "Standardized Containment & Stability Testing for Herbal Medicines", "skill": "Standardized Drug Packaging & Containment", "dept": "All Departments", "yr": 3, "pre": 32.0, "post": 61.5, "status": "Completed"},
            {"title": "Ayurvedic Pharmacopoeia Protocols (API) & Regulatory Compliance", "skill": "Ayurvedic Pharmacopoeia Protocols (API)", "dept": "Dravyaguna Vijnana (Herbal Pharmacology)", "yr": 3, "pre": 52.0, "post": 78.4, "status": "Ongoing"},
            {"title": "Automated Formulation Informatics & Herb-Drug Safety Analysis", "skill": "Automated AYUSH Formulation Intelligence", "dept": "Ayurvedic Quality Control & Drug Standardization", "yr": 3, "pre": 28.0, "post": 64.0, "status": "Upcoming"}
        ]

        for ws in workshops_seed:
            w = Workshop(
                institution_id=primary_inst.id,
                title=ws["title"],
                description=f"Intensive 24-hour hands-on technical workshop focused on {ws['skill']}.",
                target_skill_name=ws["skill"],
                target_department=ws["dept"],
                target_year=ws["yr"],
                target_proficiency_max=50.0,
                duration_hours=24,
                start_date="01 Oct 2026",
                end_date="20 Oct 2026",
                pre_avg_score=ws["pre"],
                post_avg_score=ws["post"],
                status=ws["status"]
            )
            db.add(w)
            db.flush()

            # Seed registrations
            for st in all_students[:10]:
                db.add(WorkshopRegistration(
                    workshop_id=w.id,
                    student_id=st.id,
                    pre_score=round(random.uniform(ws["pre"] - 5, ws["pre"] + 5), 1),
                    post_score=round(random.uniform(ws["post"] - 5, ws["post"] + 5), 1) if ws["status"] == "Completed" else None,
                    attended=True,
                    completed=(ws["status"] == "Completed")
                ))

        # 11. Seed National AYUSH Challenges & Hackathons (SIH 2026)
        db.add(Hackathon(
            title="Smart India AYUSH Challenge 2026 (SIH26044)",
            organizer="Ministry of AYUSH / CCRAS",
            theme="AYUSH Generic Medicine Quality Intelligence & Standardization Platform",
            problem_statements_json=[
                "SIH26044: Real AYUSH Generic Medicine Quality Intelligence & Skill Verification Platform with closed-loop national telemetry",
                "SIH26045: Automated Substandard Drug Detection & Manufacturer Verification System",
                "SIH26046: Adaptive Monograph Assessment Engine for Regional AYUSH Institutions"
            ],
            eligibility="All BAMS, MD (Ayurveda), B.Pharm (Ayurveda) & AYUSH Institution Scholars",
            registration_deadline="15 Nov 2026",
            start_date="22 Nov 2026",
            end_date="24 Nov 2026",
            prizes="₹1,00,000 Cash Prize + Direct Fast-Track Interview with Top AYUSH Pharmaceutical Partners",
            is_national=True,
            status="Active"
        ))

        db.add(Hackathon(
            title="National AYUSH Phytochemical Formulation Grand Challenge",
            organizer="Pharmacopoeia Commission for Indian Medicine & Homoeopathy (PCIM&H)",
            theme="Classical Formulation Optimization & Biomarker Standardization",
            problem_statements_json=["Standardized classical formulation extraction workflows for rural medicine manufacturing units"],
            eligibility="All AYUSH Scholars & Pharmaceutical Innovators",
            registration_deadline="30 Nov 2026",
            start_date="05 Dec 2026",
            end_date="07 Dec 2026",
            prizes="₹2,00,000 + AYUSH Incubation & Regulatory Support",
            is_national=True,
            status="Active"
        ))

        # 12. Seed Government Opportunities & Aggregated Schemes
        gov_opps = [
            {
                "title": "National AYUSH Apprenticeship & GMP Training Scheme (NAATS 2026)",
                "agency": "Ministry of AYUSH / Pharmacopoeia Commission",
                "type": "Apprenticeship",
                "dept": "Ayurvedic Quality Assurance & Manufacturing Division",
                "location": "Pan-India",
                "stipend": "₹12,500 / month + National AYUSH Certification",
                "eligibility": "BAMS / B.Pharm (Ayurveda) Graduates (2025/2026)",
                "skills": ["Ashwagandha", "Triphala", "AYUSH Good Manufacturing Practice (GMP)"],
                "url": "https://ayush.gov.in/apprenticeships",
                "deadline": "15 Dec 2026"
            },
            {
                "title": "Ministry of AYUSH - Dabur National Phytochemical Quality Internship",
                "agency": "CCRAS Virtual Research & Quality Internships",
                "type": "Government Internship",
                "dept": "Drug Standardization & Phytochemical Cell",
                "location": "Virtual / Pan-India",
                "stipend": "₹15,000 / month + Ministry of AYUSH Digital Badge",
                "eligibility": "2nd, 3rd, 4th Year BAMS & Ayurvedic Pharmacy Students",
                "skills": ["Ashwagandha", "Phytochemical Assay & Analysis", "Ayurvedic Pharmacopoeia Protocols (API)"],
                "url": "https://internship.ayush.gov.in",
                "deadline": "30 Nov 2026"
            },
            {
                "title": "AYUSH Pharmacovigilance & Drug Safety Fellowship",
                "agency": "National Pharmacovigilance Coordination Centre (NPvCC - AYUSH)",
                "type": "Fellowship",
                "dept": "Adverse Drug Reaction & Safety Monitoring Centre",
                "location": "New Delhi / Remote",
                "stipend": "₹25,000 / month",
                "eligibility": "Final Year & Post-Graduate Ayurvedic Scholars",
                "skills": ["Pharmacovigilance & Drug Safety Monitoring", "AYUSH Good Manufacturing Practice (GMP)", "Standardized Drug Packaging & Containment"],
                "url": "https://ayushsuraksha.gov.in/fellowships",
                "deadline": "10 Jan 2027"
            }
        ]

        for go in gov_opps:
            db.add(GovernmentOpportunity(
                title=go["title"],
                agency=go["agency"],
                opportunity_type=go["type"],
                department=go["dept"],
                location=go["location"],
                stipend_or_pay=go["stipend"],
                eligibility=go["eligibility"],
                skills_json=go["skills"],
                application_url=go["url"],
                deadline=go["deadline"],
                is_active=True,
                is_demo_source=True
            ))

        # 13. Seed Initial Notifications
        db.add(Notification(
            user_id=u_student.id,
            title="🎯 Interview Scheduled: AYUSH Medicine Quality & Phytochemical Analyst",
            message="Dabur AYUSH Life Sciences has invited you for Technical Round 1 on 10 Sep 2026.",
            notification_type="InterviewInvite",
            action_url="/student/applications",
            is_read=False
        ))
        db.add(Notification(
            user_id=u_student.id,
            title="🚀 Smart India AYUSH Challenge 2026 Announced!",
            message="Smart India AYUSH Challenge 2026 problem statements are live. Form your team now!",
            notification_type="Hackathon",
            action_url="/student/hackathons",
            is_read=False
        ))
        db.add(Notification(
            user_id=u_recruiter.id,
            title="New Top Candidate Match: Rahul Sharma (94.2%)",
            message="Rahul Sharma applied for AYUSH Medicine Quality & Phytochemical Analyst and satisfies 100% of Critical Skills.",
            notification_type="ApplicationStatus",
            action_url="/recruiter/jobs",
            is_read=False
        ))

        db.commit()
        print("Database seeded successfully with all 30+ entities and realistic demo accounts!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
