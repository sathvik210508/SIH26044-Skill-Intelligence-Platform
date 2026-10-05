from typing import Dict, Any

class ReadinessEngine:
    """
    Computes Institution and Department Platform Readiness Score (PRS) using:
    PRS = 0.35*S + 0.25*P + 0.20*I + 0.10*T + 0.10*A
    
    where:
    - S: Average verified skill proficiency of students
    - P: Placement performance / placement rate
    - I: Internship participation rate
    - T: Training & workshop completion rate
    - A: Industry alignment index with national skill demand
    """

    def calculate_readiness(
        self,
        avg_skill_score: float,       # S: 0-100
        placement_rate: float,        # P: 0-100
        internship_rate: float,       # I: 0-100
        training_completion_rate: float,  # T: 0-100
        industry_alignment_score: float   # A: 0-100
    ) -> Dict[str, Any]:
        s_contrib = avg_skill_score * 0.35
        p_contrib = placement_rate * 0.25
        i_contrib = internship_rate * 0.20
        t_contrib = training_completion_rate * 0.10
        a_contrib = industry_alignment_score * 0.10

        total_prs = s_contrib + p_contrib + i_contrib + t_contrib + a_contrib
        total_prs = min(100.0, max(0.0, round(total_prs, 1)))

        tier = "Tier 1 — High Readiness" if total_prs >= 80 else ("Tier 2 — Moderate Readiness" if total_prs >= 60 else "Tier 3 — Focus / Intervention Needed")

        return {
            "readiness_score": total_prs,
            "readiness_tier": tier,
            "formula": "PRS = 0.35(S) + 0.25(P) + 0.20(I) + 0.10(T) + 0.10(A)",
            "components": {
                "S_skill_proficiency": {"raw": round(avg_skill_score, 1), "weight": 0.35, "contribution": round(s_contrib, 1)},
                "P_placement_rate": {"raw": round(placement_rate, 1), "weight": 0.25, "contribution": round(p_contrib, 1)},
                "I_internship_rate": {"raw": round(internship_rate, 1), "weight": 0.20, "contribution": round(i_contrib, 1)},
                "T_training_rate": {"raw": round(training_completion_rate, 1), "weight": 0.10, "contribution": round(t_contrib, 1)},
                "A_industry_alignment": {"raw": round(industry_alignment_score, 1), "weight": 0.10, "contribution": round(a_contrib, 1)}
            },
            "summary": f"Calculated Platform Readiness Score of {total_prs}% ({tier})."
        }

readiness_engine = ReadinessEngine()
