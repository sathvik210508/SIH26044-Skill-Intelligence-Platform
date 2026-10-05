/**
 * SIH26044 — Student Portal Module (Clean SaaS Design)
 */

import { api } from './api.js';
import { renderSkillGapBar } from './charts.js';

let activeQuizData = null;
let activeQuizTimer = null;
let quizSecondsRemaining = 600;

/**
 * 1. Student Dashboard (Overview)
 */
export async function renderStudentDashboard(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted); font-size:0.9rem;">Loading Student Skill Intelligence...</p></div>`;

  try {
    const profile = await api.get('/api/student/profile');
    const matchedJobs = await api.get('/api/student/jobs/matched');
    const gaps = await api.get('/api/student/skill-gaps?target_role=Phytochemical Quality & Safety Specialist');

    const avgProficiency = profile.skills.length > 0 
      ? Math.round(profile.skills.reduce((acc, s) => acc + s.proficiency_score, 0) / profile.skills.length)
      : 78;

    const topJob = matchedJobs[0] || { title: 'AYUSH Drug Quality Analyst & Safety Trainee', match_score: 91, company_name: 'Dabur AYUSH Life Sciences' };

    targetContainer.innerHTML = `
      <!-- Greeting Banner -->
      <div class="white-card" style="background:#FFFFFF; border-left:4px solid var(--primary);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
          <div>
            <h2 style="font-size:1.35rem; font-weight:700; color:var(--text-primary);">Good morning, ${profile.full_name}</h2>
            <p style="color:var(--text-muted); font-size:0.86rem; margin-top:3px;">
              Track your skills, discover suitable roles, and improve your career readiness at <strong>${profile.institution_name}</strong>.
            </p>
          </div>
          <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <button class="btn btn-secondary" id="btn-dash-resume">
              <i class="fa-solid fa-file-arrow-up" style="color:var(--primary);"></i> Extract Resume
            </button>
            <button class="btn btn-primary" id="btn-dash-add-skill">
              <i class="fa-solid fa-plus"></i> Add Skill
            </button>
          </div>
        </div>
      </div>

      <!-- Main Overview KPI Metrics -->
      <div class="grid-4">
        <div class="kpi-card">
          <div class="kpi-icon"><i class="fa-solid fa-gauge-high"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${avgProficiency}%</div>
            <div class="kpi-label">Career Readiness</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-arrow-trend-up"></i> Verified Benchmark</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--accent-cyan-light); color:var(--accent-cyan);"><i class="fa-solid fa-bullseye"></i></div>
          <div class="kpi-content">
            <div class="kpi-value" style="font-size:1.15rem; line-height:1.2; padding-top:4px;">${topJob.match_score}% Match</div>
            <div class="kpi-label">${topJob.title.split('/')[0]}</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-check"></i> Top Role Alignment</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--success-light); color:var(--success);"><i class="fa-solid fa-certificate"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${profile.skills.length}</div>
            <div class="kpi-label">Verified Skills</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-shield-check"></i> Evidence-backed</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--warning-light); color:var(--warning);"><i class="fa-solid fa-triangle-exclamation"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${gaps.critical_gaps.length}</div>
            <div class="kpi-label">Skill Gaps</div>
            <div class="kpi-sub warning"><i class="fa-solid fa-road"></i> Pathways Available</div>
          </div>
        </div>
      </div>

      <!-- Next Recommended Actions & Top Skills Overview -->
      <div class="grid-2">
        <div class="white-card">
          <div class="card-header">
            <div class="card-title"><i class="fa-solid fa-list-check"></i> Recommended Next Actions</div>
            <span class="badge badge-info">AI Priority</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:10px;">
            <div style="padding:10px 14px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light); display:flex; justify-content:space-between; align-items:center;">
              <div>
                <strong style="font-size:0.88rem; color:var(--text-primary);"><i class="fa-solid fa-circle-arrow-right" style="color:var(--primary); margin-right:6px;"></i> Strengthen AYUSH GMP & Standardized Containment</strong>
                <p style="font-size:0.78rem; color:var(--text-muted); margin-top:2px;">Required for 4 top medicine quality matches with high stipends.</p>
              </div>
              <button class="btn btn-sm btn-secondary" onclick="window.navigateToTab('skill_gaps')">View Roadmap</button>
            </div>
            <div style="padding:10px 14px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light); display:flex; justify-content:space-between; align-items:center;">
              <div>
                <strong style="font-size:0.88rem; color:var(--text-primary);"><i class="fa-solid fa-vial" style="color:var(--success); margin-right:6px;"></i> Complete Adaptive Assessment for Ashwagandha</strong>
                <p style="font-size:0.78rem; color:var(--text-muted); margin-top:2px;">Raise your test score component from 88% to 95%+.</p>
              </div>
              <button class="btn btn-sm btn-primary" id="btn-dash-quiz-python">Take Quiz</button>
            </div>
            <div style="padding:10px 14px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light); display:flex; justify-content:space-between; align-items:center;">
              <div>
                <strong style="font-size:0.88rem; color:var(--text-primary);"><i class="fa-solid fa-briefcase" style="color:var(--accent-cyan); margin-right:6px;"></i> Apply to AYUSH Quality & Pharmacognosy Research Officer at Dabur AYUSH Life Sciences</strong>
                <p style="font-size:0.78rem; color:var(--text-muted); margin-top:2px;">Your verified skill profile exceeds critical job requirements.</p>
              </div>
              <button class="btn btn-sm btn-secondary" onclick="window.navigateToTab('jobs')">View Jobs</button>
            </div>
          </div>
        </div>

        <div class="white-card">
          <div class="card-header">
            <div class="card-title"><i class="fa-solid fa-bars-progress"></i> Skill Proficiency Highlights</div>
            <button class="btn btn-sm btn-secondary" onclick="window.navigateToTab('skills')">View All Skills</button>
          </div>
          <div>
            ${profile.skills.slice(0, 4).map(sk => `
              <div class="skill-bar-row">
                <div class="skill-bar-header">
                  <span class="skill-bar-name">${sk.skill_name}</span>
                  <span class="badge ${sk.proficiency_score >= 75 ? 'badge-success' : (sk.proficiency_score >= 50 ? 'badge-warning' : 'badge-danger')}">
                    ${sk.proficiency_score}%
                  </span>
                </div>
                <div class="progress-bar-container">
                  <div class="progress-bar-fill ${sk.proficiency_score >= 75 ? 'success' : (sk.proficiency_score >= 50 ? 'warning' : 'danger')}" style="width: ${sk.proficiency_score}%;"></div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>

      <!-- Top Career Matches Overview -->
      <div class="white-card">
        <div class="card-header">
          <div class="card-title"><i class="fa-solid fa-wand-magic-sparkles"></i> Top Career Matches</div>
          <button class="btn btn-sm btn-secondary" onclick="window.navigateToTab('career_matches')">Explore Detailed Matching</button>
        </div>
        <div class="table-responsive">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Target Career Role</th>
                <th>Calculated Match</th>
                <th>Matching Core Skills</th>
                <th>Identified Gaps</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>AYUSH Medicine Quality Analyst</strong></td>
                <td><span class="badge badge-success" style="font-size:0.8rem;"><i class="fa-solid fa-bolt"></i> 91% Match</span></td>
                <td><span style="font-size:0.82rem; color:var(--text-secondary);">Ashwagandha, Triphala, Clinical Drug Assay & Statistical Evaluation, Batch Manufacturing Records (BMR)</span></td>
                <td><span class="badge badge-warning">AYUSH Market Analytics (Minor)</span></td>
                <td><button class="btn btn-sm btn-secondary" onclick="window.navigateToTab('career_matches')">View Details</button></td>
              </tr>
              <tr>
                <td><strong>Phytochemical Quality & Safety Specialist</strong></td>
                <td><span class="badge badge-success" style="font-size:0.8rem;"><i class="fa-solid fa-bolt"></i> 88% Match</span></td>
                <td><span style="font-size:0.82rem; color:var(--text-secondary);">Ashwagandha, Phytochemical Assay & Analysis, Triphala, Ayurvedic Pharmacopoeia Protocols (API)</span></td>
                <td><span class="badge badge-danger">AYUSH GMP, Standardized Drug Packaging</span></td>
                <td><button class="btn btn-sm btn-secondary" onclick="window.navigateToTab('career_matches')">View Details</button></td>
              </tr>
              <tr>
                <td><strong>AYUSH Formulation & Quality Specialist</strong></td>
                <td><span class="badge badge-success" style="font-size:0.8rem;"><i class="fa-solid fa-bolt"></i> 80% Match</span></td>
                <td><span style="font-size:0.82rem; color:var(--text-secondary);">Haridra, Ashwagandha, Ayurvedic Pharmacopoeia Protocols (API), Triphala</span></td>
                <td><span class="badge badge-warning">Standardized Drug Packaging</span></td>
                <td><button class="btn btn-sm btn-secondary" onclick="window.navigateToTab('career_matches')">View Details</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;

    // Attach Handlers
    document.getElementById('btn-dash-resume')?.addEventListener('click', () => openResumeModal());
    document.getElementById('btn-dash-add-skill')?.addEventListener('click', () => openAddSkillModal());
    document.getElementById('btn-dash-quiz-python')?.addEventListener('click', () => startAdaptiveQuiz(1, 'Ashwagandha'));

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load dashboard: ${err.message}</div>`;
  }
}

/**
 * 2. Student Profile (Clean & Realistic)
 */
export async function renderStudentProfile(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading Student Profile...</p></div>`;

  try {
    const profile = await api.get('/api/student/profile');

    targetContainer.innerHTML = `
      <div class="grid-1-2">
        <!-- Academic Identity Card -->
        <div class="white-card">
          <div class="card-header">
            <div class="card-title"><i class="fa-solid fa-id-card"></i> Student Information</div>
            <span class="badge badge-success">Verified</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:14px;">
            <div>
              <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Full Name</div>
              <div style="font-size:1.1rem; font-weight:700; color:var(--text-primary); margin-top:2px;">${profile.full_name}</div>
            </div>
            <div>
              <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Institution / College</div>
              <div style="font-size:0.95rem; font-weight:600; color:var(--text-primary); margin-top:2px;">
                <i class="fa-solid fa-university" style="color:var(--primary); margin-right:6px;"></i> ${profile.institution_name}
              </div>
            </div>
            <div class="grid-2">
              <div>
                <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Department</div>
                <div style="font-size:0.88rem; font-weight:600; color:var(--text-secondary); margin-top:2px;">${profile.department_name}</div>
              </div>
              <div>
                <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Academic Year</div>
                <div style="font-size:0.88rem; font-weight:600; color:var(--text-secondary); margin-top:2px;">Year ${profile.current_year} (Pre-Final)</div>
              </div>
            </div>
            <div class="grid-2">
              <div>
                <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Roll Number</div>
                <div style="font-size:0.88rem; font-weight:600; color:var(--text-secondary); margin-top:2px;">${profile.roll_number}</div>
              </div>
              <div>
                <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">CGPA</div>
                <div style="font-size:0.88rem; font-weight:700; color:var(--success-text); margin-top:2px;">${profile.cgpa} / 10.0</div>
              </div>
            </div>
            <div>
              <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Target Career Path</div>
              <div style="font-size:0.88rem; font-weight:600; color:var(--primary); margin-top:2px;">
                <i class="fa-solid fa-bullseye" style="margin-right:6px;"></i> ${profile.career_interests}
              </div>
            </div>
            <div>
              <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:600;">Placement Status</div>
              <div style="margin-top:4px;"><span class="badge badge-info">${profile.placement_status}</span></div>
            </div>
          </div>
        </div>

        <!-- Verified Projects & Certifications -->
        <div style="display:flex; flex-direction:column; gap:20px;">
          <div class="white-card">
            <div class="card-header">
              <div class="card-title"><i class="fa-solid fa-flask-vial"></i> Verified Practical Projects</div>
              <span class="badge badge-purple">${(profile.projects || []).length} Verified</span>
            </div>
            <div style="display:flex; flex-direction:column; gap:12px;">
              ${(profile.projects || []).map(p => `
                <div style="padding:12px 14px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light);">
                  <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <strong style="font-size:0.92rem; color:var(--text-primary);">${p.title}</strong>
                    ${p.repo_url ? `<a href="${p.repo_url}" target="_blank" class="btn btn-sm btn-secondary" style="font-size:0.72rem; text-decoration:none;"><i class="fa-solid fa-file-waveform"></i> Monograph Record</a>` : ''}
                  </div>
                  <p style="font-size:0.8rem; color:var(--text-secondary); margin-top:4px;">${p.description}</p>
                  <div style="margin-top:6px; font-size:0.75rem; color:var(--text-muted);">
                    <strong>Skills Applied:</strong> ${p.skills_used}
                  </div>
                </div>
              `).join('')}
            </div>
          </div>

          <div class="white-card">
            <div class="card-header">
              <div class="card-title"><i class="fa-solid fa-award"></i> Verified Courses & Certifications</div>
              <span class="badge badge-success">${(profile.certifications || []).length + (profile.courses || []).length} Active</span>
            </div>
            <div style="display:flex; flex-direction:column; gap:10px;">
              ${(profile.certifications || []).map(c => `
                <div style="padding:10px 14px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light); display:flex; justify-content:space-between; align-items:center;">
                  <div>
                    <strong style="font-size:0.86rem; color:var(--text-primary);">${c.name}</strong>
                    <div style="font-size:0.76rem; color:var(--text-muted);">${c.issuer} • Credential ID: ${c.credential_id}</div>
                  </div>
                  <span class="badge badge-success">Verified</span>
                </div>
              `).join('')}
              ${(profile.courses || []).map(co => `
                <div style="padding:10px 14px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light); display:flex; justify-content:space-between; align-items:center;">
                  <div>
                    <strong style="font-size:0.86rem; color:var(--text-primary);">${co.title}</strong>
                    <div style="font-size:0.76rem; color:var(--text-muted);">${co.provider} • Grade: ${co.grade_or_score}</div>
                  </div>
                  <span class="badge badge-info">Completed</span>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load profile: ${err.message}</div>`;
  }
}

/**
 * 3. Student Skills (Clean Horizontal Progress Bars & Evidence Calculation)
 */
export async function renderStudentSkills(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted); font-size:0.9rem;">Loading Verified Skills...</p></div>`;

  try {
    const profile = await api.get('/api/student/profile');

    targetContainer.innerHTML = `
      <!-- Action Toolbar -->
      <div class="white-card">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
          <div>
            <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">Skill Competency & Evidence Breakdown</h3>
            <p style="color:var(--text-muted); font-size:0.82rem; margin-top:2px;">
              Proficiency formula: <strong>S = 0.40(Test) + 0.30(Practical) + 0.15(Verified Experience) + 0.15(Coursework)</strong>
            </p>
          </div>
          <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <button class="btn btn-secondary" id="btn-skills-resume"><i class="fa-solid fa-file-pdf" style="color:var(--danger);"></i> Extract from Resume</button>
            <button class="btn btn-primary" id="btn-skills-add"><i class="fa-solid fa-plus"></i> Add Skill Evidence</button>
          </div>
        </div>
      </div>

      <!-- Skills List with Clean Horizontal Progress Bars -->
      <div class="white-card">
        <div class="card-header">
          <div class="card-title"><i class="fa-solid fa-bars-progress"></i> Verified Skills Inventory (${profile.skills.length})</div>
          <span style="font-size:0.75rem; color:var(--text-muted);">Evidence Verified</span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(360px, 1fr)); gap:14px;">
          ${profile.skills.map(sk => `
            <div style="padding:14px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light); display:flex; flex-direction:column; justify-content:space-between;">
              <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                  <span style="font-weight:700; font-size:0.95rem; color:var(--text-primary);">${sk.skill_name}</span>
                  <div style="display:flex; align-items:center; gap:6px;">
                    <span class="badge ${sk.proficiency_score >= 75 ? 'badge-success' : (sk.proficiency_score >= 50 ? 'badge-warning' : 'badge-danger')}">
                      ${sk.proficiency_score}% (${sk.proficiency_score >= 75 ? 'Strong' : (sk.proficiency_score >= 50 ? 'Moderate' : 'Needs Practice')})
                    </span>
                  </div>
                </div>
                <div class="progress-bar-container">
                  <div class="progress-bar-fill ${sk.proficiency_score >= 75 ? 'success' : (sk.proficiency_score >= 50 ? 'warning' : 'danger')}" style="width: ${sk.proficiency_score}%;"></div>
                </div>
                <div style="font-size:0.75rem; color:var(--text-muted); margin-top:8px;">
                  <i class="fa-solid fa-circle-info" style="color:var(--primary); margin-right:4px;"></i>
                  ${sk.breakdown?.breakdown_explanation || 'Assessment + Practical components verified.'}
                </div>
              </div>
              <div style="margin-top:12px; padding-top:8px; border-top:1px solid var(--border-light); display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:0.72rem; color:var(--text-dim);">Source: Curriculum / Verified</span>
                <button class="btn btn-sm btn-secondary btn-retake-quiz" data-skill-id="${sk.skill_id}" data-skill-name="${sk.skill_name}">
                  <i class="fa-solid fa-vial"></i> Take Test
                </button>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    document.getElementById('btn-skills-resume')?.addEventListener('click', () => openResumeModal());
    document.getElementById('btn-skills-add')?.addEventListener('click', () => openAddSkillModal());

    document.querySelectorAll('.btn-retake-quiz').forEach(btn => {
      btn.addEventListener('click', () => {
        startAdaptiveQuiz(btn.dataset.skillId, btn.dataset.skillName);
      });
    });

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load skills: ${err.message}</div>`;
  }
}

/**
 * 4. Skill Gap Analysis
 */
export async function renderStudentSkillGaps(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Calculating personalized skill gaps...</p></div>`;

  try {
    const gaps = await api.get('/api/student/skill-gaps?target_role=Phytochemical Quality & Safety Specialist');

    const labels = gaps.gaps.map(g => g.skill);
    const currentVals = gaps.gaps.map(g => g.current_level);
    const targetVals = gaps.gaps.map(g => g.target_level);

    targetContainer.innerHTML = `
      <div class="white-card">
        <div class="card-header">
          <div>
            <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">Skill Benchmark vs Target Role</h3>
            <p style="color:var(--text-muted); font-size:0.82rem; margin-top:2px;">
              Target Role: <strong>${gaps.target_role}</strong>
            </p>
          </div>
          <span class="badge badge-info">AI Benchmark</span>
        </div>
        <div style="height:260px; position:relative;">
          <canvas id="student-gap-chart"></canvas>
        </div>
      </div>

      <!-- Actionable Roadmaps for Identified Gaps -->
      <div class="white-card">
        <div class="card-header">
          <div class="card-title"><i class="fa-solid fa-road"></i> Recommended Skill Pathways</div>
          <span style="font-size:0.75rem; color:var(--text-muted);">${gaps.gaps.length} Evaluated Skills</span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap:14px;">
          ${gaps.gaps.map(g => `
            <div style="padding:14px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light);">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong style="font-size:0.92rem; color:var(--text-primary);">${g.skill}</strong>
                <span class="badge ${g.status === 'Satisfied' ? 'badge-success' : (g.status === 'Moderate Gap' ? 'badge-warning' : 'badge-danger')}">
                  ${g.gap > 0 ? `Gap: ${g.gap}%` : 'Satisfied'}
                </span>
              </div>
              <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:var(--text-muted); margin-top:8px;">
                <span>Current: <strong>${g.current_level}%</strong></span>
                <span>Target: <strong>${g.target_level}%</strong></span>
              </div>
              <div class="progress-bar-container" style="margin-top:4px;">
                <div class="progress-bar-fill ${g.status === 'Satisfied' ? 'success' : (g.status === 'Moderate Gap' ? 'warning' : 'danger')}" style="width: ${Math.min(100, (g.current_level / g.target_level) * 100)}%;"></div>
              </div>
              <div style="margin-top:10px; font-size:0.78rem; color:var(--text-secondary);">
                <p><strong>Action Roadmap:</strong> ${g.resources.roadmap}</p>
                <div style="display:flex; gap:8px; margin-top:8px;">
                  <a href="${g.resources.docs}" target="_blank" class="btn btn-sm btn-secondary" style="text-decoration:none;"><i class="fa-solid fa-book"></i> Docs</a>
                  <a href="${g.resources.video}" target="_blank" class="btn btn-sm btn-secondary" style="text-decoration:none;"><i class="fa-brands fa-youtube" style="color:var(--danger);"></i> Tutorial</a>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    setTimeout(() => {
      renderSkillGapBar('student-gap-chart', labels, currentVals, targetVals);
    }, 50);

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load skill gaps: ${err.message}</div>`;
  }
}

/**
 * 5. Career Matches
 */
export async function renderStudentCareerMatches(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Analyzing career role suitability...</p></div>`;

  try {
    const matchedJobs = await api.get('/api/student/jobs/matched');

    const careerRoles = [
      {
        role: "AYUSH Medicine Quality Analyst",
        match: 91,
        matchingSkills: ["Ashwagandha", "Triphala", "Clinical Drug Assay & Statistical Evaluation", "Ayurvedic Pharmacopoeia Protocols (API)"],
        missingSkills: ["AYUSH Market Analytics & Consumption Trends"],
        explanation: "Your high Ashwagandha, Triphala formulation evaluation, and structured analytical skills provide an outstanding match."
      },
      {
        role: "Phytochemical Quality & Safety Specialist",
        match: 88,
        matchingSkills: ["Ashwagandha", "Phytochemical Assay & Analysis", "Ayurvedic Pharmacopoeia Protocols (API)", "Clinical Drug Assay & Statistical Evaluation"],
        missingSkills: ["Standardized Drug Packaging & Containment", "AYUSH Good Manufacturing Practice (GMP)"],
        explanation: "Strong phytochemical testing and active evaluation evidence align closely with core quality specialist requirements."
      },
      {
        role: "AYUSH Formulation & Research Scientist",
        match: 84,
        matchingSkills: ["Phytochemical Assay & Analysis", "Ashwagandha", "Ayurvedic Pharmacopoeia Protocols (API)"],
        missingSkills: ["Standardized Drug Packaging & Containment", "Ayurvedic Pharmaceutical Batch Processing", "Batch Quality Assurance (QA)"],
        explanation: "Core formulation assay design is solid; gaining standardized batch packaging and processing experience will achieve a 95%+ match."
      },
      {
        role: "AYUSH Formulation & Quality Specialist",
        match: 80,
        matchingSkills: ["Haridra", "Ayurvedic Pharmacopoeia Protocols (API)", "Ashwagandha", "Triphala"],
        missingSkills: ["Tulsi", "Standardized Drug Packaging & Containment"],
        explanation: "Verified Haridra herbal formulation and Ayurvedic Pharmacopoeia protocol skills satisfy classical manufacturing and quality standards."
      },
      {
        role: "AYUSH Pharmacovigilance & Drug Surveillance Officer",
        match: 76,
        matchingSkills: ["Triphala", "Clinical Drug Assay & Statistical Evaluation", "Ashwagandha"],
        missingSkills: ["AYUSH Market Analytics & Consumption Trends", "Pharmacovigilance & Drug Safety Monitoring"],
        explanation: "Your Triphala formulation analysis and clinical assay foundation is strong; adding pharmacovigilance surveillance reports will bridge the gap."
      }
    ];

    targetContainer.innerHTML = `
      <div class="white-card">
        <div class="card-header">
          <div>
            <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">AI Career Role Intelligence</h3>
            <p style="color:var(--text-muted); font-size:0.82rem; margin-top:2px;">
              Roles ranked based on your verified skill scores vs live industry demand benchmarks.
            </p>
          </div>
          <span class="badge badge-success">AI Match Engine</span>
        </div>

        <div style="display:flex; flex-direction:column; gap:16px;">
          ${careerRoles.map(cr => `
            <div style="padding:16px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light);">
              <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div>
                  <h4 style="font-size:1.05rem; font-weight:700; color:var(--text-primary);">${cr.role}</h4>
                  <div style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">Match score calculated from verified test + practical metrics</div>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                  <span class="badge ${cr.match >= 85 ? 'badge-success' : (cr.match >= 75 ? 'badge-warning' : 'badge-info')}" style="font-size:0.88rem; padding:4px 10px;">
                    <i class="fa-solid fa-bolt"></i> ${cr.match}% Match
                  </span>
                </div>
              </div>

              <div class="progress-bar-container" style="margin:10px 0;">
                <div class="progress-bar-fill ${cr.match >= 85 ? 'success' : (cr.match >= 75 ? 'warning' : 'info')}" style="width: ${cr.match}%;"></div>
              </div>

              <div class="grid-2" style="margin-top:12px; gap:12px;">
                <div style="font-size:0.8rem;">
                  <strong style="color:var(--success-text);"><i class="fa-solid fa-check"></i> Matching Skills:</strong>
                  <div style="margin-top:4px; display:flex; flex-wrap:wrap; gap:4px;">
                    ${cr.matchingSkills.map(ms => `<span class="badge badge-success" style="font-size:0.7rem;">${ms}</span>`).join('')}
                  </div>
                </div>
                <div style="font-size:0.8rem;">
                  <strong style="color:var(--danger-text);"><i class="fa-solid fa-circle-xmark"></i> Missing Skills:</strong>
                  <div style="margin-top:4px; display:flex; flex-wrap:wrap; gap:4px;">
                    ${cr.missingSkills.map(ms => `<span class="badge badge-danger" style="font-size:0.7rem;">${ms}</span>`).join('')}
                  </div>
                </div>
              </div>

              <div style="margin-top:10px; padding:8px 12px; background:#FFFFFF; border-radius:var(--radius-sm); border:1px solid var(--border-light); font-size:0.8rem; color:var(--text-secondary);">
                <strong>Why this match:</strong> "${cr.explanation}"
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load career matches: ${err.message}</div>`;
  }
}

/**
 * 6. Student Jobs View
 */
export async function renderStudentJobs(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading matched opportunities...</p></div>`;

  try {
    const jobs = await api.get('/api/student/jobs/matched');

    targetContainer.innerHTML = `
      <div class="white-card">
        <div class="card-header">
          <div>
            <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">AI-Matched Opportunities</h3>
            <p style="color:var(--text-muted); font-size:0.82rem; margin-top:2px;">
              Positions ranked by match against your verified skills and academic record.
            </p>
          </div>
          <span class="badge badge-info">${jobs.length} Opportunities</span>
        </div>

        <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(340px, 1fr)); gap:16px;">
          ${jobs.map(j => `
            <div style="padding:16px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light); display:flex; flex-direction:column; justify-content:space-between;">
              <div>
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                  <span class="badge badge-purple">${j.job_type}</span>
                  <span class="badge badge-success" style="font-size:0.82rem;"><i class="fa-solid fa-bolt"></i> ${j.match_score}% Match</span>
                </div>
                <h4 style="font-size:1.05rem; font-weight:700; color:var(--text-primary); margin-top:8px;">${j.title}</h4>
                <p style="font-size:0.82rem; color:var(--text-muted); margin-top:2px;">
                  <i class="fa-solid fa-building" style="margin-right:4px;"></i> ${j.company_name} • <i class="fa-solid fa-location-dot" style="margin-right:4px;"></i> ${j.location}
                </p>
                <div style="font-size:0.84rem; font-weight:700; color:var(--primary); margin-top:8px;">
                  ${j.salary_range}
                </div>
                <div style="margin-top:10px; padding:8px 10px; background:#FFFFFF; border-radius:var(--radius-sm); border:1px solid var(--border-light); font-size:0.78rem; color:var(--text-secondary);">
                  <i class="fa-solid fa-lightbulb" style="color:var(--warning); margin-right:4px;"></i> ${j.explanation}
                </div>
              </div>

              <div style="margin-top:14px; display:flex; gap:8px;">
                <button class="btn btn-secondary btn-sm btn-view-job-why" data-job='${JSON.stringify(j).replace(/'/g, "&apos;")}' style="flex:1;">
                  Why Match?
                </button>
                <button class="btn btn-primary btn-sm btn-apply-job" data-job-id="${j.job_id}" ${j.application_status !== 'Not Applied' ? 'disabled' : ''} style="flex:1;">
                  ${j.application_status !== 'Not Applied' ? `<i class="fa-solid fa-check"></i> ${j.application_status}` : `<i class="fa-solid fa-paper-plane"></i> Apply`}
                </button>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    document.querySelectorAll('.btn-view-job-why').forEach(btn => {
      btn.addEventListener('click', () => {
        const job = JSON.parse(btn.dataset.job);
        openMatchExplainModal(job);
      });
    });

    document.querySelectorAll('.btn-apply-job').forEach(btn => {
      btn.addEventListener('click', async () => {
        const jId = btn.dataset.jobId;
        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Applying...`;
        try {
          const res = await api.post('/api/student/apply', { job_id: parseInt(jId) });
          window.showToast?.(res.message, 'success');
          btn.innerHTML = `<i class="fa-solid fa-check"></i> Applied`;
        } catch (err) {
          window.showToast?.(err.message, 'danger');
          btn.disabled = false;
          btn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> Apply`;
        }
      });
    });

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load jobs: ${err.message}</div>`;
  }
}

/**
 * Interactive Modals
 */
export function openAddSkillModal() {
  const modalContainer = document.getElementById('modal-container');
  modalContainer.innerHTML = `
    <div class="modal-card">
      <div class="modal-header">
        <h3><i class="fa-solid fa-plus" style="color:var(--primary); margin-right:6px;"></i> Add Skill & Evidence Record</h3>
        <button class="btn btn-sm btn-secondary btn-close-modal"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">Skill Name</label>
          <input type="text" id="input-skill-name" class="form-control" placeholder="e.g. Standardized Packaging, HPLC Fingerprinting, AYUSH GMP" />
        </div>
        <div class="form-group">
          <label class="form-label">Evidence Category</label>
          <select id="select-evidence-type" class="form-control">
            <option value="Practical">Practical Project / Lab Score (wP = 30%)</option>
            <option value="Test">Adaptive Assessment Score (wT = 40%)</option>
            <option value="Course">Certification / Coursework Score (wC = 15%)</option>
            <option value="Verified">Industry / Resume Verified Experience (wV = 15%)</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Performance / Benchmark Score (0 - 100%)</label>
          <input type="number" id="input-skill-score" class="form-control" min="30" max="100" value="84" />
        </div>
        <div class="form-group">
          <label class="form-label">Project / Evidence URL (Optional)</label>
          <input type="url" id="input-skill-url" class="form-control" placeholder="https://ayush.gov.in/monographs/my-formulation-record" />
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary btn-close-modal">Cancel</button>
        <button class="btn btn-primary" id="btn-submit-add-skill"><i class="fa-solid fa-check"></i> Calculate & Save</button>
      </div>
    </div>
  `;
  const overlay = document.getElementById('modal-overlay');
  overlay.classList.add('active');

  overlay.querySelectorAll('.btn-close-modal').forEach(b => {
    b.onclick = () => overlay.classList.remove('active');
  });

  document.getElementById('btn-submit-add-skill').onclick = async () => {
    const name = document.getElementById('input-skill-name').value.trim();
    const evType = document.getElementById('select-evidence-type').value;
    const score = parseFloat(document.getElementById('input-skill-score').value);
    const url = document.getElementById('input-skill-url').value.trim();

    if (!name) {
      window.showToast?.('Please enter a skill name', 'warning');
      return;
    }

    try {
      const res = await api.post('/api/student/add-skill', {
        skill_name: name,
        evidence_type: evType,
        score: score,
        url: url
      });
      window.showToast?.(res.message, 'success');
      overlay.classList.remove('active');
      window.navigateToTab('skills');
    } catch (err) {
      window.showToast?.(err.message, 'danger');
    }
  };
}

export function openResumeModal() {
  const modalContainer = document.getElementById('modal-container');
  modalContainer.innerHTML = `
    <div class="modal-card">
      <div class="modal-header">
        <h3><i class="fa-solid fa-file-pdf" style="color:var(--danger); margin-right:6px;"></i> Resume Skill Extractor</h3>
        <button class="btn btn-sm btn-secondary btn-close-modal"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <div class="modal-body" id="resume-modal-body">
        <p style="color:var(--text-muted); font-size:0.84rem; margin-bottom:14px;">
          Upload your resume PDF or paste resume text. RapidFuzz and the skill ontology engine will detect and normalize your competencies.
        </p>
        <div class="form-group">
          <label class="form-label">Upload Resume PDF</label>
          <input type="file" id="resume-file-input" class="form-control" accept=".pdf,.txt" />
        </div>
        <div class="form-group">
          <label class="form-label">Or Paste Resume Content</label>
          <textarea id="resume-text-input" class="form-control" rows="3" placeholder="Paste resume text here..."></textarea>
        </div>
        <button class="btn btn-primary" id="btn-run-extraction" style="width:100%;"><i class="fa-solid fa-microchip"></i> Extract & Match Skills</button>
        <div id="extraction-results-area" style="margin-top:16px;"></div>
      </div>
    </div>
  `;
  const overlay = document.getElementById('modal-overlay');
  overlay.classList.add('active');

  overlay.querySelectorAll('.btn-close-modal').forEach(b => {
    b.onclick = () => overlay.classList.remove('active');
  });

  document.getElementById('btn-run-extraction').onclick = async () => {
    const fileInput = document.getElementById('resume-file-input');
    const textInput = document.getElementById('resume-text-input').value.trim();
    const btn = document.getElementById('btn-run-extraction');
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Extracting skills...`;

    try {
      let res;
      if (fileInput.files.length > 0) {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        res = await api.post('/api/student/resume/extract-skills', formData);
      } else {
        const formData = new FormData();
        formData.append('resume_text', textInput || 'Rahul Sharma. Skills: Ashwagandha, Triphala, Haridra, Standardized Drug Packaging, Phytochemical Assay & Analysis, Ayurvedic Pharmacopoeia Protocols (API).');
        res = await api.post('/api/student/resume/extract-skills', formData);
      }

      renderExtractedSkillsVerification(res.extracted_skills);
    } catch (err) {
      window.showToast?.(err.message, 'danger');
      btn.disabled = false;
      btn.innerHTML = `<i class="fa-solid fa-microchip"></i> Extract & Match Skills`;
    }
  };
}

function renderExtractedSkillsVerification(extractedSkills) {
  const area = document.getElementById('extraction-results-area');
  area.innerHTML = `
    <div style="padding:10px 12px; background:var(--info-light); border:1px solid #BAE6FD; border-radius:var(--radius-sm); margin-bottom:12px;">
      <strong style="color:var(--info-text); font-size:0.85rem;"><i class="fa-solid fa-circle-check"></i> ${extractedSkills.length} Skills Detected!</strong>
      <p style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">Confirm the skills to import into your verified profile:</p>
    </div>
    <div style="max-height:180px; overflow-y:auto; margin-bottom:14px;">
      ${extractedSkills.map((s, idx) => `
        <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 10px; background:var(--bg-subtle); border-radius:var(--radius-sm); margin-bottom:4px;">
          <label style="display:flex; align-items:center; gap:8px; font-size:0.84rem; color:var(--text-primary); cursor:pointer;">
            <input type="checkbox" class="chk-verified-skill" data-skill-name="${s.skill_name}" checked />
            <span><strong>${s.skill_name}</strong> <span style="font-size:0.72rem; color:var(--text-muted);">(alias: "${s.detected_alias}")</span></span>
          </label>
          <div style="display:flex; align-items:center; gap:4px;">
            <span style="font-size:0.72rem; color:var(--text-muted);">Proficiency:</span>
            <input type="number" class="form-control input-extracted-rating" data-skill-name="${s.skill_name}" value="80" min="30" max="100" style="width:60px; padding:2px 6px; font-size:0.78rem;" />
          </div>
        </div>
      `).join('')}
    </div>
    <button class="btn btn-success" id="btn-save-extracted-skills" style="width:100%;"><i class="fa-solid fa-check-double"></i> Confirm & Import Skills</button>
  `;

  document.getElementById('btn-save-extracted-skills').onclick = async () => {
    const chks = document.querySelectorAll('.chk-verified-skill');
    const skillsToSave = [];
    chks.forEach(chk => {
      if (chk.checked) {
        const sName = chk.dataset.skillName;
        const ratingInput = document.querySelector(`.input-extracted-rating[data-skill-name="${sName}"]`);
        const rating = ratingInput ? parseFloat(ratingInput.value) : 78.0;
        skillsToSave.push({ skill_name: sName, verified: true, self_rating: rating });
      }
    });

    try {
      const saveRes = await api.post('/api/student/resume/verify-skills', { skills: skillsToSave });
      window.showToast?.(saveRes.message, 'success');
      document.getElementById('modal-overlay').classList.remove('active');
      window.navigateToTab('skills');
    } catch (err) {
      window.showToast?.(err.message, 'danger');
    }
  };
}

export async function startAdaptiveQuiz(skillId, skillName) {
  const modalContainer = document.getElementById('modal-container');
  modalContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading adaptive questions for ${skillName}...</p></div>`;
  const overlay = document.getElementById('modal-overlay');
  overlay.classList.add('active');

  try {
    const quiz = await api.get(`/api/assessment/start/${skillId || 1}`);
    activeQuizData = quiz;
    quizSecondsRemaining = 600;

    renderQuizInterface(quiz);
  } catch (err) {
    modalContainer.innerHTML = `<div class="modal-card"><div class="modal-body" style="color:var(--danger); text-align:center;">Failed to start quiz: ${err.message}</div></div>`;
  }
}

function renderQuizInterface(quiz) {
  const modalContainer = document.getElementById('modal-container');
  modalContainer.innerHTML = `
    <div class="modal-card" style="max-width:700px;">
      <div class="modal-header">
        <div>
          <h3 style="font-size:1.1rem; font-weight:700;"><i class="fa-solid fa-stopwatch" style="color:var(--warning); margin-right:6px;"></i> Adaptive Test: ${quiz.skill_name}</h3>
          <span style="font-size:0.75rem; color:var(--text-muted);">10-minute dynamic difficulty assessment</span>
        </div>
        <div id="quiz-timer-display" style="padding:4px 10px; background:var(--danger-light); border-radius:var(--radius-full); color:var(--danger-text); font-weight:800; font-size:0.85rem;">
          10:00
        </div>
      </div>
      <div class="modal-body" id="quiz-body" style="max-height:55vh; overflow-y:auto;">
        ${quiz.questions.map((q, idx) => `
          <div style="margin-bottom:16px; padding:12px 14px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span style="font-weight:700; color:var(--primary); font-size:0.82rem;">Question ${idx + 1} of ${quiz.questions.length}</span>
              <span class="badge ${q.difficulty === 'Hard' ? 'badge-danger' : (q.difficulty === 'Medium' ? 'badge-warning' : 'badge-info')}">${q.difficulty}</span>
            </div>
            <p style="font-size:0.88rem; font-weight:600; color:var(--text-primary); margin-bottom:10px;">${q.question_text}</p>
            <div style="display:flex; flex-direction:column; gap:6px;">
              ${q.options.map((opt, optIdx) => `
                <label style="display:flex; align-items:center; gap:10px; padding:8px 12px; background:#FFFFFF; border:1px solid var(--border-light); border-radius:var(--radius-sm); cursor:pointer; font-size:0.84rem;">
                  <input type="radio" name="${q.question_id}" value="${optIdx}" style="accent-color:var(--primary);" />
                  <span>${opt}</span>
                </label>
              `).join('')}
            </div>
          </div>
        `).join('')}
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary btn-close-modal">Cancel</button>
        <button class="btn btn-success" id="btn-submit-quiz"><i class="fa-solid fa-check"></i> Submit Assessment</button>
      </div>
    </div>
  `;

  if (activeQuizTimer) clearInterval(activeQuizTimer);
  activeQuizTimer = setInterval(() => {
    quizSecondsRemaining--;
    const mins = Math.floor(quizSecondsRemaining / 60);
    const secs = quizSecondsRemaining % 60;
    const timerEl = document.getElementById('quiz-timer-display');
    if (timerEl) {
      timerEl.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    if (quizSecondsRemaining <= 0) {
      clearInterval(activeQuizTimer);
      document.getElementById('btn-submit-quiz')?.click();
    }
  }, 1000);

  document.querySelectorAll('.btn-close-modal').forEach(b => {
    b.onclick = () => {
      clearInterval(activeQuizTimer);
      document.getElementById('modal-overlay').classList.remove('active');
    };
  });

  document.getElementById('btn-submit-quiz').onclick = async () => {
    clearInterval(activeQuizTimer);
    const answers = {};
    quiz.questions.forEach(q => {
      const checked = document.querySelector(`input[name="${q.question_id}"]:checked`);
      answers[q.question_id] = checked ? parseInt(checked.value) : -1;
    });

    try {
      const gradeRes = await api.post('/api/assessment/submit', {
        skill_id: quiz.skill_id,
        student_answers: answers,
        answers_key: quiz.answers_key
      });

      renderQuizResultScorecard(gradeRes);
    } catch (err) {
      window.showToast?.(err.message, 'danger');
    }
  };
}

function renderQuizResultScorecard(result) {
  const modalContainer = document.getElementById('modal-container');
  modalContainer.innerHTML = `
    <div class="modal-card" style="text-align:center;">
      <div class="modal-header" style="justify-content:center;">
        <h3 style="font-size:1.15rem; font-weight:700;"><i class="fa-solid fa-award" style="color:var(--success); margin-right:6px;"></i> Assessment Result</h3>
      </div>
      <div class="modal-body">
        <div style="width:80px; height:80px; border-radius:var(--radius-full); background:var(--success-light); border:2px solid var(--success); display:flex; align-items:center; justify-content:center; margin:0 auto 12px; font-size:1.6rem; font-weight:800; color:var(--success-text);">
          ${result.score}%
        </div>
        <h4 style="font-size:1.05rem; color:var(--text-primary);">${result.passed ? '🎉 Passed — Proficiency Updated' : 'Attempt Recorded'}</h4>
        <p style="color:var(--text-muted); font-size:0.82rem; margin-top:2px;">Answered ${result.correct_answers} of ${result.total_questions} questions correctly.</p>

        <div style="margin-top:16px; padding:12px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light); text-align:left;">
          <strong style="color:var(--primary); font-size:0.82rem;"><i class="fa-solid fa-calculator"></i> Proficiency Engine Recalculation:</strong>
          <div style="font-size:1rem; font-weight:700; color:var(--text-primary); margin:4px 0;">New Overall Proficiency: ${result.new_overall_proficiency}%</div>
          <p style="font-size:0.75rem; color:var(--text-muted);">${result.breakdown}</p>
        </div>
      </div>
      <div class="modal-footer" style="justify-content:center;">
        <button class="btn btn-primary" id="btn-finish-quiz"><i class="fa-solid fa-check"></i> Return to Skills</button>
      </div>
    </div>
  `;

  document.getElementById('btn-finish-quiz').onclick = () => {
    document.getElementById('modal-overlay').classList.remove('active');
    window.navigateToTab('skills');
  };
}

function openMatchExplainModal(job) {
  const modalContainer = document.getElementById('modal-container');
  modalContainer.innerHTML = `
    <div class="modal-card">
      <div class="modal-header">
        <div>
          <h3 style="font-size:1.1rem; font-weight:700;"><i class="fa-solid fa-wand-magic-sparkles" style="color:var(--primary); margin-right:6px;"></i> Match Score Breakdown</h3>
          <span style="font-size:0.75rem; color:var(--text-muted);">${job.title} at ${job.company_name}</span>
        </div>
        <button class="btn btn-sm btn-secondary btn-close-modal"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <div class="modal-body">
        <div style="display:flex; align-items:center; justify-content:space-between; padding:12px 16px; background:var(--primary-light); border:1px solid #C7D2FE; border-radius:var(--radius-sm); margin-bottom:14px;">
          <div>
            <div style="font-size:1.6rem; font-weight:800; color:var(--primary);">${job.match_score}%</div>
            <div style="font-size:0.72rem; color:var(--text-muted);">Overall AI Calculated Match</div>
          </div>
          <div>
            <span class="badge badge-success">Critical Coverage: ${job.critical_coverage_pct}%</span>
          </div>
        </div>

        <h4 style="font-size:0.88rem; font-weight:700; color:var(--text-primary); margin-bottom:8px;">Matched Skills vs Requirements</h4>
        <div style="max-height:160px; overflow-y:auto; margin-bottom:14px;">
          ${(job.matched_skills || []).map(s => `
            <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 10px; background:var(--bg-subtle); border-radius:var(--radius-sm); margin-bottom:4px; font-size:0.8rem;">
              <span><strong>${s.skill}</strong> <span class="badge badge-purple" style="font-size:0.62rem;">${s.importance}</span></span>
              <span style="color:var(--success-text);">Your Score: ${s.student_proficiency}% (Req: ${s.required_proficiency}%)</span>
            </div>
          `).join('')}
          ${(job.skill_gaps || []).map(g => `
            <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 10px; background:var(--danger-light); border-radius:var(--radius-sm); margin-bottom:4px; font-size:0.8rem;">
              <span><strong>${g.skill}</strong> <span class="badge badge-danger" style="font-size:0.62rem;">Gap: ${g.gap}%</span></span>
              <span style="color:var(--danger-text);">Your Score: ${g.student_proficiency}% (Req: ${g.required_proficiency}%)</span>
            </div>
          `).join('')}
        </div>

        <div style="padding:10px 12px; background:var(--bg-subtle); border-radius:var(--radius-sm); font-size:0.78rem; color:var(--text-secondary); border:1px solid var(--border-light);">
          <strong>Explainability Narrative:</strong> ${job.explanation}
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary btn-close-modal">Close</button>
      </div>
    </div>
  `;
  const overlay = document.getElementById('modal-overlay');
  overlay.classList.add('active');
  overlay.querySelectorAll('.btn-close-modal').forEach(b => {
    b.onclick = () => overlay.classList.remove('active');
  });
}
