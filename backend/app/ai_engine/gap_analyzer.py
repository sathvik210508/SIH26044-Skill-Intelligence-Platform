from typing import List, Dict, Any, Optional

TARGET_CAREER_BENCHMARKS = {
    "AYUSH Medicine Quality Analyst": {
        "Triphala": 85.0,
        "Ashwagandha": 75.0,
        "AYUSH Market Analytics & Consumption Trends": 80.0,
        "Batch Manufacturing Records (BMR)": 90.0,
        "Clinical Drug Assay & Statistical Evaluation": 85.0
    },
    "Phytochemical Quality & Safety Specialist": {
        "Ashwagandha": 85.0,
        "Phytochemical Assay & Analysis": 80.0,
        "HPLC Standardization & Fingerprinting": 75.0,
        "Triphala": 80.0,
        "Clinical Drug Assay & Statistical Evaluation": 85.0,
        "Automated AYUSH Formulation Intelligence": 70.0
    },
    "AYUSH Formulation & Quality Specialist": {
        "Turmeric / Curcumin": 85.0,
        "Haridra": 80.0,
        "Ashwagandha": 75.0,
        "Triphala": 75.0,
        "Standardized Drug Packaging & Containment": 65.0,
        "Batch Quality Assurance (QA)": 60.0
    },
    "AYUSH Good Manufacturing Practice (GMP) Officer": {
        "AYUSH Good Manufacturing Practice (GMP)": 85.0,
        "Batch Quality Assurance (QA)": 85.0,
        "Standardized Drug Packaging & Containment": 80.0,
        "Ayurvedic Pharmaceutical Batch Processing": 75.0,
        "Ashwagandha": 70.0
    },
    "AYUSH Pharmacovigilance & Drug Surveillance Officer": {
        "Pharmacovigilance & Drug Safety Monitoring": 85.0,
        "Clinical Drug Assay & Statistical Evaluation": 80.0,
        "Ashwagandha": 70.0,
        "AYUSH Good Manufacturing Practice (GMP)": 65.0
    },
    "Data Analyst": {
        "Triphala": 85.0,
        "Ashwagandha": 75.0,
        "Power BI": 80.0,
        "Excel": 90.0,
        "Data Analysis": 85.0
    }
}

ROLE_ALIASES = {
    "data scientist / ai engineer": "Phytochemical Quality & Safety Specialist",
    "machine learning engineer": "Phytochemical Quality & Safety Specialist",
    "full stack developer": "AYUSH Formulation & Quality Specialist",
    "cloud & devops engineer": "AYUSH Good Manufacturing Practice (GMP) Officer",
    "data analyst": "AYUSH Medicine Quality Analyst",
    "business intelligence analyst": "AYUSH Medicine Quality Analyst",
    "cybersecurity specialist": "AYUSH Pharmacovigilance & Drug Surveillance Officer"
}

SKILL_ALIAS_LOOKUP = {
    "ashwagandha": ["python", "py", "withania somnifera"],
    "triphala": ["sql", "mysql", "postgresql", "sqlite"],
    "turmeric / curcumin": ["turmeric", "javascript", "js", "curcumin"],
    "haridra": ["react", "reactjs", "curcuma longa"],
    "phytochemical assay & analysis": ["machine learning", "ml", "phytochemistry"],
    "hplc standardization & fingerprinting": ["deep learning", "dl", "hplc"],
    "ayush good manufacturing practice (gmp)": ["cloud computing", "cloud", "gmp"],
    "batch quality assurance (qa)": ["aws", "quality assurance"],
    "standardized drug packaging & containment": ["docker", "packaging"],
    "ayurvedic pharmaceutical batch processing": ["kubernetes", "k8s"],
    "ayush market analytics & consumption trends": ["power bi", "powerbi", "analytics"],
    "batch manufacturing records (bmr)": ["excel", "ms excel", "bmr"],
    "clinical drug assay & statistical evaluation": ["data analysis", "pandas", "drug assay"],
    "automated ayush formulation intelligence": ["genai", "generative ai", "llms"],
    "pharmacovigilance & drug safety monitoring": ["cybersecurity", "safety"]
}

SKILL_LEARNING_RESOURCES = {
    "Ashwagandha": {
        "roadmap": "Botanical Identification -> Classical Pharmacology (Rasa/Guna/Virya/Vipaka) -> Therapeutic Formulations -> Clinical Standardization",
        "docs": "https://ayush.gov.in/",
        "course": "Ayurvedic Pharmacognosy & Clinical Pharmacology (National Institute of Ayurveda)",
        "video": "https://www.youtube.com/results?search_query=ashwagandha+clinical+monograph",
        "practice": "Pharmacopeial Quality Assessment & Standardization"
    },
    "Triphala": {
        "roadmap": "Individual Myrobalan Identification -> Standard Formulation Proportions -> Anulomana & Rasayana Therapeutics -> Quality Control Standards",
        "docs": "https://ayush.gov.in/",
        "course": "Classical Ayurvedic Formulations & Practice (CCRAS)",
        "video": "https://www.youtube.com/results?search_query=triphala+classical+ayurvedic+formulation",
        "practice": "AFI Formulation Protocol & Phytochemical Profiling"
    },
    "Turmeric / Curcumin": {
        "roadmap": "Curcuma Longa Identification -> Curcuminoid Extraction & Quantification -> Anti-inflammatory Therapeutics -> Bioavailability Protocols",
        "docs": "https://ayush.gov.in/",
        "course": "Herbal Phytochemistry & Therapeutic Applications (CCRAS)",
        "video": "https://www.youtube.com/results?search_query=turmeric+curcumin+ayurveda",
        "practice": "Curcumin Assay & Piperine Bio-enhancement Labs"
    },
    "Haridra": {
        "roadmap": "Botanical Specimen Grading -> Curcuminoid Extraction -> HPLC Purity Assay -> Topical & Oral Formulation Standards",
        "docs": "https://ayush.gov.in/",
        "course": "Classical Dravyaguna & Single-Drug Pharmacology (AIIA)",
        "video": "https://www.youtube.com/results?search_query=haridra+ayurvedic+monograph",
        "practice": "Phytochemical Fingerprinting Laboratory"
    },
    "Phytochemical Assay & Analysis": {
        "roadmap": "Active Phytochemical Screening -> Thin Layer Chromatography (TLC) -> Quantitative Spectrophotometry -> Monograph Limits",
        "docs": "https://pcimh.gov.in/",
        "course": "Advanced Herbal Quality Control & Phytochemical Testing (NIA)",
        "video": "https://www.youtube.com/results?search_query=phytochemical+assay+herbal+medicine",
        "practice": "HPTLC / UV-Vis Spectrophotometry Laboratory Protocols"
    },
    "AYUSH Good Manufacturing Practice (GMP)": {
        "roadmap": "Schedule T Regulatory Framework -> Cleanroom Maintenance -> Batch Manufacturing Records (BMR) -> In-Process Quality Auditing",
        "docs": "https://ayush.gov.in/",
        "course": "AYUSH GMP & Pharmaceutical Plant Operations Certification",
        "video": "https://www.youtube.com/results?search_query=ayush+gmp+guidelines+schedule+t",
        "practice": "GMP Inspection Simulation & SOP Formulation"
    },
    "Standardized Drug Packaging & Containment": {
        "roadmap": "Container-Closure Integrity -> Moisture Barrier Standardization -> Accelerated Stability Studies -> Tamper-Evident Labelling",
        "docs": "https://pcimh.gov.in/",
        "course": "Pharmaceutical Packaging & Stability Testing in AYUSH Drugs",
        "video": "https://www.youtube.com/results?search_query=pharmaceutical+packaging+herbal+medicine",
        "practice": "Packaging Compatibility & Shelf-Life Assessment"
    },
    "AYUSH Market Analytics & Consumption Trends": {
        "roadmap": "Herbal Supply Chain Tracking -> Generic Drug Demand Aggregation -> Pricing Telemetry -> Export Trends Analytics",
        "docs": "https://ayush.gov.in/",
        "course": "AYUSH Healthcare Economics & Pharmaceutical Supply Chain (CCRAS)",
        "video": "https://www.youtube.com/results?search_query=ayush+market+trends+and+export",
        "practice": "AYUSH Market Demand Analytics Dashboarding"
    },
    "Automated AYUSH Formulation Intelligence": {
        "roadmap": "Classical Samhita Digitization -> Monograph Retrieval Augmented Generation -> Adulterant Risk Detection -> Pharmacopoeia Cross-Referencing",
        "docs": "https://ayush.gov.in/",
        "course": "Digital Health & AYUSH Informatics (National Institute of Ayurveda)",
        "video": "https://www.youtube.com/results?search_query=ayush+informatics+and+digital+health",
        "practice": "Classical Monograph Formulation Risk Screening"
    }
}

class GapAnalyzer:
    """
    Analyzes student skill profile against target career profiles and benchmarks.
    Identifies strengths, weaknesses, critical gaps, and learning roadmaps.
    """

    def analyze_student_gaps(
        self,
        student_skills: Dict[str, float],
        target_role: str = "Phytochemical Quality & Safety Specialist"
    ) -> Dict[str, Any]:
        benchmarks = TARGET_CAREER_BENCHMARKS.get(target_role)
        if not benchmarks:
            norm_role = target_role.strip().lower()
            resolved_role = ROLE_ALIASES.get(norm_role, target_role)
            benchmarks = TARGET_CAREER_BENCHMARKS.get(resolved_role) or TARGET_CAREER_BENCHMARKS["Phytochemical Quality & Safety Specialist"]
        
        strongest_skills = []
        weakest_skills = []
        gaps = []
        
        # Check benchmarks
        for skill_name, target_score in benchmarks.items():
            current_score = student_skills.get(skill_name.lower(), 0.0)
            if current_score == 0.0:
                # Check aliases
                aliases = SKILL_ALIAS_LOOKUP.get(skill_name.lower(), [])
                for al in aliases:
                    if al in student_skills and student_skills[al] > 0.0:
                        current_score = student_skills[al]
                        break
            gap = max(0.0, target_score - current_score)
            
            gap_item = {
                "skill": skill_name,
                "current_level": round(current_score, 1),
                "target_level": round(target_score, 1),
                "gap": round(gap, 1),
                "status": "Satisfied" if gap <= 5.0 else ("Moderate Gap" if gap <= 25.0 else "Critical Gap"),
                "resources": SKILL_LEARNING_RESOURCES.get(skill_name, {
                    "roadmap": f"Master {skill_name} core concepts through hands-on documentation and projects.",
                    "docs": f"https://www.google.com/search?q={skill_name}+official+documentation",
                    "course": f"Learn {skill_name} on NPTEL / Coursera",
                    "video": f"https://www.youtube.com/results?search_query={skill_name}+full+course",
                    "practice": "Build practical showcase projects"
                })
            }
            
            if current_score >= 75.0:
                strongest_skills.append({
                    "skill": skill_name,
                    "proficiency": round(current_score, 1)
                })
            elif current_score < 50.0:
                weakest_skills.append({
                    "skill": skill_name,
                    "proficiency": round(current_score, 1)
                })
                
            gaps.append(gap_item)

        # Sort gaps by urgency (largest gap first)
        gaps.sort(key=lambda x: x["gap"], reverse=True)
        critical_gaps = [g for g in gaps if g["status"] == "Critical Gap"]

        # Recommended order of improvement
        learning_order = [
            f"Phase 1: Focus on {gaps[0]['skill']} (Gap: {gaps[0]['gap']}%)" if gaps else "Maintain proficiency",
            f"Phase 2: Reinforce {gaps[1]['skill']} (Gap: {gaps[1]['gap']}%)" if len(gaps) > 1 else "",
            f"Phase 3: Upgrade {gaps[2]['skill']} to target benchmark" if len(gaps) > 2 else ""
        ]
        learning_order = [p for p in learning_order if p]

        return {
            "target_role": target_role,
            "benchmarks": benchmarks,
            "gaps": gaps,
            "critical_gaps": critical_gaps,
            "strongest_skills": strongest_skills,
            "weakest_skills": weakest_skills,
            "recommended_learning_order": learning_order,
            "total_gap_points": round(sum(g["gap"] for g in gaps), 1)
        }

gap_analyzer = GapAnalyzer()
