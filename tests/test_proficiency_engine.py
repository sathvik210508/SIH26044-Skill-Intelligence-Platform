import pytest
from app.ai_engine.proficiency_engine import ProficiencyEngine, DEFAULT_WEIGHTS

def test_full_evidence_calculation():
    engine = ProficiencyEngine()
    # Ashwagandha: Assessment = 88, Practical = 82, Verified Experience = 80, Course = 90
    # Expected S = 0.40*88 + 0.30*82 + 0.15*80 + 0.15*90 = 35.2 + 24.6 + 12.0 + 13.5 = 85.3
    res = engine.calculate_proficiency(
        test_score=88.0,
        practical_score=82.0,
        verified_score=80.0,
        course_score=90.0
    )
    assert res["proficiency_score"] == 85.3
    assert len(res["missing_components"]) == 0
    assert "Assessment Test" in res["breakdown_explanation"]

def test_missing_evidence_dynamic_normalization():
    engine = ProficiencyEngine()
    # Student has Test=88 and Practical=82, but no Verified Experience and no Course
    # Base weights: T=0.40, P=0.30 -> Total = 0.70
    # Normalized: T = 0.40/0.70 = 0.5714, P = 0.30/0.70 = 0.4286
    # S = 0.5714*88 + 0.4286*82 = 50.28 + 35.14 = 85.4
    res = engine.calculate_proficiency(
        test_score=88.0,
        practical_score=82.0,
        verified_score=None,
        course_score=None
    )
    assert res["proficiency_score"] == 85.4
    assert "verified" in res["missing_components"]
    assert "course" in res["missing_components"]
    assert "Weights dynamically normalized" in res["breakdown_explanation"]

def test_single_evidence_normalization():
    engine = ProficiencyEngine()
    # Student has only course score 90.0
    res = engine.calculate_proficiency(
        test_score=None,
        practical_score=None,
        verified_score=None,
        course_score=90.0
    )
    assert res["proficiency_score"] == 90.0

def test_zero_evidence():
    engine = ProficiencyEngine()
    res = engine.calculate_proficiency(None, None, None, None)
    assert res["proficiency_score"] == 0.0
