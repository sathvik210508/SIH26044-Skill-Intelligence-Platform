from typing import Dict, Any, Optional

DEFAULT_WEIGHTS = {
    "test": 0.40,       # w_T: Adaptive Assessment Score
    "practical": 0.30,  # w_P: Practical / Project / Lab Score
    "verified": 0.15,   # w_V: Verified Experience / Resume / Endorsement Score
    "course": 0.15      # w_C: Course / Certification Score
}

class ProficiencyEngine:
    """
    Skill Proficiency Calculation Engine implementing:
    S = w_T * T + w_P * P + w_V * V + w_C * C
    
    Includes evidence-aware dynamic rebalancing to prevent unfair penalization
    when certifications or other single components are missing.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or DEFAULT_WEIGHTS

    def calculate_proficiency(
        self,
        test_score: Optional[float] = None,
        practical_score: Optional[float] = None,
        verified_score: Optional[float] = None,
        course_score: Optional[float] = None,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        weights = custom_weights or self.weights
        
        scores = {
            "test": test_score,
            "practical": practical_score,
            "verified": verified_score,
            "course": course_score
        }
        
        # Filter available (non-None) evidence scores
        available = {k: v for k, v in scores.items() if v is not None and v >= 0}
        
        if not available:
            return {
                "proficiency_score": 0.0,
                "weights_used": weights,
                "normalized_weights": {},
                "available_components": [],
                "missing_components": list(scores.keys()),
                "breakdown_explanation": "No evidence or assessment recorded for this skill."
            }

        total_available_weight = sum(weights[k] for k in available.keys())
        
        if total_available_weight == 0:
            total_available_weight = 1.0
            normalized_weights = {k: 1.0 / len(available) for k in available.keys()}
        else:
            normalized_weights = {k: weights[k] / total_available_weight for k in available.keys()}
            
        final_score = 0.0
        contributions = {}
        explanation_parts = []
        
        labels = {
            "test": "Assessment Test",
            "practical": "Projects & Practical",
            "verified": "Verified Experience",
            "course": "Courses & Certifications"
        }

        for k, val in available.items():
            norm_w = normalized_weights[k]
            contrib = val * norm_w
            final_score += contrib
            contributions[k] = {
                "raw_score": round(val, 1),
                "base_weight": round(weights[k], 2),
                "normalized_weight": round(norm_w, 3),
                "contribution": round(contrib, 1)
            }
            explanation_parts.append(
                f"{labels[k]} ({round(val, 1)}% × {round(norm_w * 100, 1)}% = {round(contrib, 1)}%)"
            )

        final_score = min(100.0, max(0.0, round(final_score, 1)))
        missing = [k for k, v in scores.items() if v is None]
        
        explanation = " + ".join(explanation_parts)
        if missing:
            missing_labels = [labels[m] for m in missing]
            explanation += f". (Weights dynamically normalized across available evidence; missing {', '.join(missing_labels)})."

        return {
            "proficiency_score": final_score,
            "weights_used": weights,
            "normalized_weights": normalized_weights,
            "available_components": list(available.keys()),
            "missing_components": missing,
            "contributions": contributions,
            "breakdown_explanation": explanation
        }

proficiency_engine = ProficiencyEngine()
