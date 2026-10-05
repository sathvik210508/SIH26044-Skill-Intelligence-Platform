import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.models.models import User, Student, Job, Application, Workshop

client = TestClient(app)

def test_auth_demo_login():
    # Test 1-click demo login for all 4 roles
    for role in ["STUDENT", "RECRUITER", "INSTITUTION", "ADMIN"]:
        res = client.post(f"/api/auth/demo-login/{role}")
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["role"] == role

def test_student_endpoints():
    # Login as Student
    login_res = client.post("/api/auth/demo-login/STUDENT")
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Profile
    p_res = client.get("/api/student/profile", headers=headers)
    assert p_res.status_code == 200
    p_data = p_res.json()
    assert p_data["full_name"] == "Rahul Sharma"
    assert len(p_data["skills"]) > 0

    # 2. Add Skill (+ Add Skill)
    add_res = client.post("/api/student/add-skill", json={
        "skill_name": "Kubernetes",
        "evidence_type": "Practical",
        "score": 85.0,
        "description": "Deployed scalable clusters in production lab."
    }, headers=headers)
    assert add_res.status_code == 200
    assert add_res.json()["proficiency_score"] > 0

    # 3. Matched Jobs
    jobs_res = client.get("/api/student/jobs/matched", headers=headers)
    assert jobs_res.status_code == 200
    jobs = jobs_res.json()
    assert len(jobs) > 0
    assert "match_score" in jobs[0]
    assert "matched_skills" in jobs[0]

    # 4. Skill Gaps
    gap_res = client.get("/api/student/skill-gaps?target_role=Data Scientist / AI Engineer", headers=headers)
    assert gap_res.status_code == 200
    assert len(gap_res.json()["gaps"]) > 0

def test_recruiter_endpoints():
    # Login as Recruiter
    login_res = client.post("/api/auth/demo-login/RECRUITER")
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Profile & Verification
    prof_res = client.get("/api/recruiter/profile", headers=headers)
    assert prof_res.status_code == 200
    assert prof_res.json()["company"]["verification"]["verification_status"] == "Verified"

    # 2. Create Job with Dynamic Skill Matrix
    job_create = client.post("/api/recruiter/jobs", json={
        "title": "Cloud Solutions Architect",
        "description": "Designing mission-critical distributed systems.",
        "job_type": "Full-Time",
        "location": "Bengaluru",
        "salary_min": 16.0,
        "salary_max": 24.0,
        "deadline": "30 Dec 2026",
        "eligibility_cgpa": 7.0,
        "eligibility_departments": "CSE, IT, AI & DS",
        "skills_matrix": [
            {"skill_name": "Cloud Computing", "required_proficiency": 80.0, "importance_weight": "Critical"},
            {"skill_name": "Docker", "required_proficiency": 75.0, "importance_weight": "High"},
            {"skill_name": "Ashwagandha", "required_proficiency": 70.0, "importance_weight": "Medium"}
        ]
    }, headers=headers)
    assert job_create.status_code == 200
    job_id = job_create.json()["job_id"]

    # 3. AI Candidate Ranking & Explainability
    cand_res = client.get(f"/api/recruiter/jobs/{job_id}/candidates", headers=headers)
    assert cand_res.status_code == 200
    candidates = cand_res.json()
    assert len(candidates) > 0
    top_student_id = candidates[0]["student_id"]

    explain_res = client.get(f"/api/recruiter/jobs/{job_id}/candidates/{top_student_id}/explain", headers=headers)
    assert explain_res.status_code == 200
    assert "overall_match_score" in explain_res.json()

def test_institution_endpoints():
    # Login as Institution TPO
    login_res = client.post("/api/auth/demo-login/INSTITUTION")
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Dashboard
    dash_res = client.get("/api/institution/dashboard", headers=headers)
    assert dash_res.status_code == 200
    assert dash_res.json()["kpis"]["total_students"] > 0

    # 2. Skill Gap Heatmap
    heat_res = client.get("/api/institution/skill-heatmap", headers=headers)
    assert heat_res.status_code == 200
    assert len(heat_res.json()["heatmap_matrix"]) > 0

    # 3. Bulk Student Creation
    bulk_res = client.post("/api/institution/bulk-create-students", json={
        "department_name": "Computer Science & Engineering",
        "current_year": 2,
        "count": 5,
        "roll_prefix": "24CS_TEST"
    }, headers=headers)
    assert bulk_res.status_code == 200
    assert bulk_res.json()["created_count"] == 5

def test_admin_and_ai_assistant():
    # Login as Admin
    admin_login = client.post("/api/auth/demo-login/ADMIN")
    token = admin_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. National Dashboard
    nat_res = client.get("/api/admin/national-dashboard", headers=headers)
    assert nat_res.status_code == 200
    assert nat_res.json()["ecosystem_summary"]["national_readiness_index"] > 70.0

    # 2. AI Assistant Navigation & Action Query
    query_res = client.post("/api/ai-assistant/query", json={
        "query": "Create workshop for Cloud Computing"
    }, headers=headers)
    assert query_res.status_code == 200
    q_data = query_res.json()
    assert q_data["action_draft"] is not None
    assert q_data["action_draft"]["action_type"] == "CREATE_WORKSHOP"

    # 3. Confirm Action Execution
    confirm_res = client.post("/api/ai-assistant/confirm-action", json={
        "action_type": q_data["action_draft"]["action_type"],
        "parameters": q_data["action_draft"]
    }, headers=headers)
    assert confirm_res.status_code == 200
    assert confirm_res.json()["success"] is True
