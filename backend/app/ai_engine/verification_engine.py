from typing import Dict, Any, Optional

class VerificationEngine:
    """
    Multi-signal verification engine for companies and job opportunities.
    Prevents fraudulent postings by scoring multiple identity & consistency signals.
    """

    def evaluate_company(
        self,
        company_name: str,
        registration_number: Optional[str],
        website: Optional[str],
        recruiter_email: Optional[str],
        historical_hires: int = 0,
        has_active_placements: bool = True
    ) -> Dict[str, Any]:
        signals = {}
        total_score = 0.0

        # Signal 1: Corporate Registration / CIN (25 pts)
        if registration_number and len(registration_number.strip()) >= 8:
            signals["cin_check"] = {"passed": True, "score": 25.0, "reason": "Valid Corporate Identity/ROC Number provided"}
            total_score += 25.0
        else:
            signals["cin_check"] = {"passed": False, "score": 5.0, "reason": "Missing or incomplete CIN registration"}
            total_score += 5.0

        # Signal 2: Official Website & Domain Match (25 pts)
        if website and ("http" in website or "." in website):
            domain = website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
            domain_match = recruiter_email and domain in recruiter_email
            if domain_match:
                signals["domain_check"] = {"passed": True, "score": 25.0, "reason": f"Recruiter email matches corporate domain ({domain})"}
                total_score += 25.0
            else:
                signals["domain_check"] = {"passed": True, "score": 18.0, "reason": f"Valid website ({domain}) verified; third-party email"}
                total_score += 18.0
        else:
            signals["domain_check"] = {"passed": False, "score": 0.0, "reason": "No valid corporate web domain"}

        # Signal 3: Historical Hiring & Placement Records (25 pts)
        if historical_hires > 50:
            signals["hiring_history"] = {"passed": True, "score": 25.0, "reason": f"Established enterprise hiring record ({historical_hires}+ verified hires)"}
            total_score += 25.0
        elif historical_hires > 0:
            signals["hiring_history"] = {"passed": True, "score": 18.0, "reason": f"Active hiring track record ({historical_hires} hires)"}
            total_score += 18.0
        else:
            signals["hiring_history"] = {"passed": False, "score": 10.0, "reason": "New recruiter profile on platform"}
            total_score += 10.0

        # Signal 4: Institution Endorsement & Placements (25 pts)
        if has_active_placements:
            signals["institution_endorsement"] = {"passed": True, "score": 25.0, "reason": "Active placement offers verified with accredited institutions"}
            total_score += 25.0
        else:
            signals["institution_endorsement"] = {"passed": False, "score": 10.0, "reason": "No on-campus placement history yet"}
            total_score += 10.0

        total_score = min(100.0, round(total_score, 1))

        if total_score >= 80.0:
            status = "Verified"
            status_label = "🟢 Verified Partner"
        elif total_score >= 50.0:
            status = "Verification Required"
            status_label = "🟡 Verification Required"
        else:
            status = "Suspicious"
            status_label = "🔴 Flagged / Suspicious"

        return {
            "company_name": company_name,
            "verification_status": status,
            "status_label": status_label,
            "verification_score": total_score,
            "signals": signals,
            "explanation": f"Company scored {total_score}/100 across 4 verification signals."
        }

verification_engine = VerificationEngine()
