from typing import List, Dict, Any, Optional

IMPORTANCE_WEIGHTS = {
    "Critical": 3.0,
    "High": 2.0,
    "Medium": 1.0,
    "Low": 0.5
}

class MatchingEngine:
    """
    Explainable AI Matching Engine.
    Matches student skill profile, academic eligibility, and practical experience
    against Recruiter Job Requirement Matrices.
    """

    def calculate_match(
        self,
        student_skills: Dict[str, float],  # {skill_name_lower: proficiency_score}
        job_requirements: List[Dict[str, Any]],  # [{skill_name, required_proficiency, importance, is_mandatory}]
        student_cgpa: float = 8.0,
        required_cgpa: float = 6.0,
        student_projects: Optional[List[Dict[str, Any]]] = None,
        student_certifications: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        if not job_requirements:
            return {
                "match_score": 100.0,
                "base_skill_match": 100.0,
                "critical_coverage_pct": 100.0,
                "matched_skills": [],
                "skill_gaps": [],
                "explanation": "No specific skill constraints required for this opportunity."
            }

        total_weight = 0.0
        weighted_skill_score = 0.0
        matched_skills = []
        skill_gaps = []
        critical_count = 0
        critical_satisfied = 0

        for req in job_requirements:
            skill_name = req.get("skill_name", "").strip()
            skill_key = skill_name.lower()
            required_prof = float(req.get("required_proficiency", 70.0))
            importance_str = req.get("importance_weight", "High")
            is_critical = (importance_str == "Critical")
            weight = IMPORTANCE_WEIGHTS.get(importance_str, 2.0)

            if is_critical:
                critical_count += 1

            student_prof = student_skills.get(skill_key, 0.0)
            if student_prof == 0.0:
                alias_lookups = {
                    "ashwagandha": "python",
                    "triphala": "sql",
                    "turmeric": "javascript",
                    "turmeric / curcumin": "javascript",
                    "tulsi": "typescript",
                    "giloy": "c++",
                    "guduchi / giloy": "c++",
                    "brahmi": "java",
                    "haridra": "react",
                    "phytochemical assay & analysis": "machine learning",
                    "hplc standardization & fingerprinting": "deep learning",
                    "ayush good manufacturing practice (gmp)": "cloud computing",
                    "batch quality assurance (qa)": "aws",
                    "standardized drug packaging & containment": "docker",
                    "ayurvedic pharmaceutical batch processing": "kubernetes",
                    "pharmacovigilance & drug safety monitoring": "cybersecurity",
                    "ayush market analytics & consumption trends": "power bi",
                    "batch manufacturing records (bmr)": "excel",
                    "clinical drug assay & statistical evaluation": "data analysis",
                    "automated ayush formulation intelligence": "genai",
                    "classical ayurvedic monograph informatics": "nlp",
                    "herbal raw material botanical inspection": "computer vision",
                    "ayush monograph & batch record versioning": "git",
                    # Reverse mappings
                    "python": "ashwagandha",
                    "sql": "triphala",
                    "javascript": "turmeric / curcumin",
                    "typescript": "tulsi",
                    "c++": "guduchi / giloy",
                    "java": "brahmi",
                    "react": "haridra",
                    "machine learning": "phytochemical assay & analysis",
                    "deep learning": "hplc standardization & fingerprinting",
                    "cloud computing": "ayush good manufacturing practice (gmp)",
                    "aws": "batch quality assurance (qa)",
                    "docker": "standardized drug packaging & containment",
                    "kubernetes": "ayurvedic pharmaceutical batch processing",
                    "cybersecurity": "pharmacovigilance & drug safety monitoring",
                    "power bi": "ayush market analytics & consumption trends",
                    "excel": "batch manufacturing records (bmr)",
                    "data analysis": "clinical drug assay & statistical evaluation",
                    "genai": "automated ayush formulation intelligence",
                    "nlp": "classical ayurvedic monograph informatics",
                    "computer vision": "herbal raw material botanical inspection",
                    "git": "ayush monograph & batch record versioning"
                }
                if skill_key in alias_lookups:
                    student_prof = student_skills.get(alias_lookups[skill_key], 0.0)
            
            # Match factor for this skill (capped at 1.0)
            if required_prof > 0:
                skill_match_ratio = min(1.0, student_prof / required_prof)
            else:
                skill_match_ratio = 1.0

            if student_prof >= (required_prof * 0.80):
                if is_critical:
                    critical_satisfied += 1

            weighted_skill_score += (skill_match_ratio * weight)
            total_weight += weight

            gap = max(0.0, required_prof - student_prof)
            
            skill_info = {
                "skill": skill_name,
                "student_proficiency": round(student_prof, 1),
                "required_proficiency": round(required_prof, 1),
                "importance": importance_str,
                "match_pct": round(skill_match_ratio * 100, 1),
                "gap": round(gap, 1)
            }

            if gap > 5.0:
                skill_gaps.append(skill_info)
            else:
                matched_skills.append(skill_info)

        base_match = (weighted_skill_score / total_weight) * 100.0 if total_weight > 0 else 0.0

        # Eligibility check
        cgpa_factor = 1.0
        if required_cgpa > 0 and student_cgpa < required_cgpa:
            cgpa_factor = max(0.7, student_cgpa / required_cgpa)

        # Practical experience / project bonus
        project_bonus = 0.0
        if student_projects:
            project_bonus = min(6.0, len(student_projects) * 2.0)

        # Certification bonus
        cert_bonus = 0.0
        if student_certifications:
            cert_bonus = min(4.0, len(student_certifications) * 1.5)

        critical_coverage = (critical_satisfied / critical_count * 100.0) if critical_count > 0 else 100.0

        final_score = (base_match * cgpa_factor) + project_bonus + cert_bonus
        final_score = min(99.5, max(10.0, round(final_score, 1)))

        # Construct explainability narrative
        matched_str = ", ".join([f"{s['skill']} ({s['match_pct']}%)" for s in matched_skills[:3]])
        gaps_str = ", ".join([f"{g['skill']} (needs +{g['gap']}%)" for g in skill_gaps[:2]])
        
        narrative_parts = []
        if matched_skills:
            narrative_parts.append(f"Strong alignment in {matched_str}")
        if skill_gaps:
            narrative_parts.append(f"Notable gaps in {gaps_str}")
        if critical_count > 0:
            narrative_parts.append(f"Satisfies {round(critical_coverage)}% of critical requirements")
        if project_bonus > 0:
            narrative_parts.append(f"+{round(project_bonus, 1)}% practical project evidence bonus")
        
        narrative = ". ".join(narrative_parts) + "."

        return {
            "match_score": final_score,
            "base_skill_match": round(base_match, 1),
            "critical_coverage_pct": round(critical_coverage, 1),
            "project_bonus": round(project_bonus, 1),
            "cert_bonus": round(cert_bonus, 1),
            "cgpa_factor": round(cgpa_factor, 2),
            "matched_skills": matched_skills,
            "skill_gaps": skill_gaps,
            "explanation": narrative
        }

matching_engine = MatchingEngine()
