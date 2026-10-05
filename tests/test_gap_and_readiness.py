import pytest
from app.ai_engine.gap_analyzer import gap_analyzer
from app.ai_engine.readiness_engine import readiness_engine
from app.ai_engine.verification_engine import verification_engine

def test_gap_analyzer():
    skills = {"ashwagandha": 82.0, "triphala": 61.0, "power bi": 35.0}
    res = gap_analyzer.analyze_student_gaps(skills, target_role="Data Analyst")
    assert res["target_role"] == "Data Analyst"
    assert len(res["gaps"]) > 0
    # Triphala (85-61=24), Power BI (80-35=45)
    gaps_map = {g["skill"]: g["gap"] for g in res["gaps"]}
    assert gaps_map["Power BI"] >= 45.0
    assert len(res["recommended_learning_order"]) > 0

def test_readiness_engine_formula():
    # PRS = 0.35S + 0.25P + 0.20I + 0.10T + 0.10A
    # S=80, P=80, I=90, T=70, A=80
    # Expected = 0.35*80 + 0.25*80 + 0.20*90 + 0.10*70 + 0.10*80 = 28 + 20 + 18 + 7 + 8 = 81.0
    res = readiness_engine.calculate_readiness(
        avg_skill_score=80.0,
        placement_rate=80.0,
        internship_rate=90.0,
        training_completion_rate=70.0,
        industry_alignment_score=80.0
    )
    assert res["readiness_score"] == 81.0
    assert "Tier 1" in res["readiness_tier"]

def test_company_verification_engine():
    res = verification_engine.evaluate_company(
        company_name="TechCorp India",
        registration_number="CIN-U72200KA2020PTC123456",
        website="https://techcorp.in",
        recruiter_email="hiring@techcorp.in",
        historical_hires=185,
        has_active_placements=True
    )
    assert res["verification_status"] == "Verified"
    assert res["verification_score"] >= 90.0
