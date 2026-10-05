import pytest
from app.ai_engine.matching_engine import MatchingEngine

def test_explainable_matching():
    engine = MatchingEngine()
    student_skills = {
        "ashwagandha": 88.0,
        "triphala": 80.0,
        "machine learning": 75.0,
        "power bi": 48.0
    }
    job_matrix = [
        {"skill_name": "Ashwagandha", "required_proficiency": 80.0, "importance_weight": "Critical"},
        {"skill_name": "Triphala", "required_proficiency": 70.0, "importance_weight": "High"},
        {"skill_name": "Power BI", "required_proficiency": 70.0, "importance_weight": "High"}
    ]

    res = engine.calculate_match(
        student_skills=student_skills,
        job_requirements=job_matrix,
        student_cgpa=8.5,
        required_cgpa=7.0,
        student_projects=[{"title": "AI Analytics App"}],
        student_certifications=[{"name": "AWS Certified"}]
    )

    assert res["match_score"] > 80.0
    assert len(res["matched_skills"]) >= 2
    assert len(res["skill_gaps"]) >= 1
    assert any(g["skill"] == "Power BI" for g in res["skill_gaps"])
    assert "Strong alignment in" in res["explanation"]
    assert res["critical_coverage_pct"] == 100.0

def test_critical_skill_missing():
    engine = MatchingEngine()
    student_skills = {"ashwagandha": 50.0}
    job_matrix = [
        {"skill_name": "Cybersecurity", "required_proficiency": 80.0, "importance_weight": "Critical"}
    ]
    res = engine.calculate_match(student_skills=student_skills, job_requirements=job_matrix)
    assert res["match_score"] < 50.0
    assert res["critical_coverage_pct"] == 0.0
