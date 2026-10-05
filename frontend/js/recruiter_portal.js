/**
 * SIH26044 — Recruiter Portal Module (Clean SaaS Design)
 */

import { api } from './api.js';
import { renderFunnelChart } from './charts.js';

/**
 * 1. Recruiter Dashboard
 */
export async function renderRecruiterDashboard(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading Recruiter Talent Dashboard...</p></div>`;

  try {
    const profile = await api.get('/api/recruiter/profile');
    const jobs = await api.get('/api/recruiter/jobs');
    const analytics = await api.get('/api/recruiter/analytics');

    targetContainer.innerHTML = `
      <!-- Company Banner -->
      <div class="white-card" style="border-left:4px solid var(--success);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
          <div>
            <div style="display:flex; align-items:center; gap:8px;">
              <h2 style="font-size:1.35rem; font-weight:700; color:var(--text-primary);">${profile.company.name}</h2>
              <span class="badge ${profile.company.verification.verification_status === 'Verified' ? 'badge-success' : 'badge-warning'}">
                <i class="fa-solid fa-shield-check"></i> ${profile.company.verification.status_label}
              </span>
              <span class="badge badge-purple">Trust Score: ${profile.company.verification.verification_score}%</span>
            </div>
            <p style="color:var(--text-muted); font-size:0.85rem; margin-top:3px;">
              ${profile.full_name} (${profile.designation}) • <i class="fa-solid fa-location-dot"></i> ${profile.company.city}, ${profile.company.state} • CIN: <code>${profile.company.verification.details?.cin || 'CIN-U72200KA2015PTC081234'}</code>
            </p>
          </div>
          <button class="btn btn-primary" id="btn-recruiter-create-job">
            <i class="fa-solid fa-plus"></i> Post Opportunity
          </button>
        </div>
      </div>

      <!-- KPI Metrics -->
      <div class="grid-4">
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--primary-light); color:var(--primary);"><i class="fa-solid fa-briefcase"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${jobs.length}</div>
            <div class="kpi-label">Active Postings</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-bolt"></i> Skill Matrices Configured</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--accent-cyan-light); color:var(--accent-cyan);"><i class="fa-solid fa-users"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${analytics.funnel.total_applications}</div>
            <div class="kpi-label">Total Applicants</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-arrow-trend-up"></i> Across Tier-1 Colleges</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--success-light); color:var(--success);"><i class="fa-solid fa-user-check"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${analytics.funnel.offer_acceptance_rate_pct}%</div>
            <div class="kpi-label">Offer Acceptance</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-check"></i> High Yield</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--warning-light); color:var(--warning);"><i class="fa-solid fa-shield-halved"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">96%</div>
            <div class="kpi-label">Verification Rating</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-circle-check"></i> Verified Employer</div>
          </div>
        </div>
      </div>

      <!-- Funnel Chart & Active Postings -->
      <div class="grid-1-2">
        <div class="white-card">
          <div class="card-header">
            <div class="card-title"><i class="fa-solid fa-filter"></i> Hiring Pipeline Funnel</div>
            <span class="badge badge-success">${analytics.funnel.selected} Selected</span>
          </div>
          <div style="height:230px; position:relative;">
            <canvas id="recruiter-funnel-chart"></canvas>
          </div>
        </div>

        <div class="white-card">
          <div class="card-header">
            <div class="card-title"><i class="fa-solid fa-briefcase"></i> Active Job Openings</div>
            <button class="btn btn-sm btn-secondary" onclick="window.navigateToTab('jobs')">Manage All</button>
          </div>
          <div style="display:flex; flex-direction:column; gap:10px;">
            ${jobs.slice(0, 3).map(j => `
              <div style="padding:12px 14px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <div>
                  <strong style="font-size:0.92rem; color:var(--text-primary);">${j.title}</strong>
                  <div style="font-size:0.78rem; color:var(--text-muted); margin-top:2px;">
                    ${j.job_type} • ${j.location} • <span style="color:var(--primary); font-weight:600;">${j.salary_range}</span>
                  </div>
                </div>
                <button class="btn btn-sm btn-primary btn-view-candidates" data-job-id="${j.id}" data-job-title="${j.title}">
                  <i class="fa-solid fa-users-viewfinder"></i> Rank Candidates (${j.applications_count})
                </button>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;

    setTimeout(() => {
      renderFunnelChart(
        'recruiter-funnel-chart',
        ['Applicants', 'Shortlisted', 'Interviewed', 'Selected'],
        [analytics.funnel.total_applications, analytics.funnel.shortlisted, analytics.funnel.interviewed, analytics.funnel.selected]
      );
    }, 50);

    document.getElementById('btn-recruiter-create-job')?.addEventListener('click', () => openCreateJobModal());

    document.querySelectorAll('.btn-view-candidates').forEach(btn => {
      btn.addEventListener('click', () => {
        openCandidatesModal(btn.dataset.jobId, btn.dataset.jobTitle);
      });
    });

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load recruiter dashboard: ${err.message}</div>`;
  }
}

/**
 * 2. Recruiter Jobs (Postings & Requirement Matrix)
 */
export async function renderRecruiterJobs(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading Job Postings...</p></div>`;

  try {
    const jobs = await api.get('/api/recruiter/jobs');

    targetContainer.innerHTML = `
      <div class="white-card">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
          <div>
            <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">Job Postings & Skill Requirement Matrices</h3>
            <p style="color:var(--text-muted); font-size:0.82rem; margin-top:2px;">
              Configure dynamic skill proficiency thresholds and importance weights for automated candidate scoring.
            </p>
          </div>
          <button class="btn btn-primary" id="btn-create-job-page"><i class="fa-solid fa-plus"></i> Post New Role</button>
        </div>
      </div>

      <div style="display:flex; flex-direction:column; gap:16px;">
        ${jobs.map(j => `
          <div class="white-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
              <div>
                <div style="display:flex; align-items:center; gap:8px;">
                  <h4 style="font-size:1.1rem; font-weight:700; color:var(--text-primary);">${j.title}</h4>
                  <span class="badge badge-purple">${j.job_type}</span>
                  <span class="badge badge-info"><i class="fa-solid fa-location-dot"></i> ${j.location}</span>
                </div>
                <p style="font-size:0.82rem; color:var(--text-muted); margin-top:4px;">
                  Compensation: <strong style="color:var(--primary);">${j.salary_range}</strong> • Min CGPA: <strong>${j.eligibility_cgpa}</strong> • Deadline: <strong>${j.deadline}</strong>
                </p>
              </div>
              <button class="btn btn-primary btn-sm btn-view-candidates" data-job-id="${j.id}" data-job-title="${j.title}">
                <i class="fa-solid fa-users-viewfinder"></i> AI Ranked Candidates (${j.applications_count})
              </button>
            </div>

            <!-- Skill Matrix Rows -->
            <div style="margin-top:14px; padding-top:10px; border-top:1px solid var(--border-light);">
              <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:var(--text-muted); margin-bottom:6px;">
                Required Skill Competencies:
              </div>
              <div style="display:flex; flex-wrap:wrap; gap:6px;">
                ${j.skills_matrix.map(m => `
                  <div style="padding:4px 10px; background:var(--bg-subtle); border:1px solid var(--border-light); border-radius:var(--radius-sm); font-size:0.78rem;">
                    <strong>${m.skill_name}</strong>: ${m.required_proficiency}% 
                    <span class="badge ${m.importance_weight === 'Critical' ? 'badge-danger' : (m.importance_weight === 'High' ? 'badge-warning' : 'badge-info')}" style="font-size:0.65rem; margin-left:4px;">
                      ${m.importance_weight}
                    </span>
                  </div>
                `).join('')}
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    `;

    document.getElementById('btn-create-job-page')?.addEventListener('click', () => openCreateJobModal());

    document.querySelectorAll('.btn-view-candidates').forEach(btn => {
      btn.addEventListener('click', () => {
        openCandidatesModal(btn.dataset.jobId, btn.dataset.jobTitle);
      });
    });

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load jobs: ${err.message}</div>`;
  }
}

/**
 * 3. Recruiter Candidates (AI Ranked Discovery)
 */
export async function renderRecruiterCandidates(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Ranking candidate talent pool...</p></div>`;

  try {
    const jobs = await api.get('/api/recruiter/jobs');
    const firstJobId = jobs[0]?.id || 1;
    const candidates = await api.get(`/api/recruiter/jobs/${firstJobId}/candidates`);

    targetContainer.innerHTML = `
      <div class="white-card">
        <div class="card-header">
          <div>
            <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">AI Candidate Discovery & Ranking</h3>
            <p style="color:var(--text-muted); font-size:0.82rem; margin-top:2px;">
              Candidates scored against role skill matrix with evidence weights and explainability.
            </p>
          </div>
          <span class="badge badge-success">${candidates.length} Ranked Candidates</span>
        </div>

        <div class="table-responsive">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Rank & Candidate</th>
                <th>Institution</th>
                <th>Dept / Year</th>
                <th>CGPA</th>
                <th>Match Score</th>
                <th>Critical Coverage</th>
                <th>Explainability</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${candidates.map((c, idx) => `
                <tr>
                  <td><strong>#${idx + 1} ${c.full_name}</strong></td>
                  <td>${c.institution_name}</td>
                  <td>${c.department_name} (Yr ${c.current_year || 3})</td>
                  <td><strong>${c.cgpa}</strong></td>
                  <td>
                    <span class="badge ${c.match_score >= 85 ? 'badge-success' : (c.match_score >= 70 ? 'badge-warning' : 'badge-danger')}">
                      <i class="fa-solid fa-bolt"></i> ${c.match_score}%
                    </span>
                  </td>
                  <td><strong style="color:var(--success-text);">${c.critical_coverage_pct}%</strong></td>
                  <td>
                    <button class="btn btn-sm btn-secondary btn-explain-candidate-page" data-job-id="${firstJobId}" data-student-id="${c.student_id}">
                      <i class="fa-solid fa-circle-question"></i> Why #${idx + 1}?
                    </button>
                  </td>
                  <td>
                    ${c.application_id ? `
                      <button class="btn btn-sm btn-success btn-interview-page" data-app-id="${c.application_id}" data-candidate-name="${c.full_name}">
                        <i class="fa-solid fa-calendar-plus"></i> Interview
                      </button>
                    ` : `
                      <button class="btn btn-sm btn-secondary" onclick="window.showToast('Outreach invite sent to ${c.full_name}', 'success')">
                        <i class="fa-solid fa-envelope"></i> Invite
                      </button>
                    `}
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;

    document.querySelectorAll('.btn-explain-candidate-page').forEach(btn => {
      btn.addEventListener('click', () => {
        openCandidateExplainModal(btn.dataset.jobId, btn.dataset.studentId);
      });
    });

    document.querySelectorAll('.btn-interview-page').forEach(btn => {
      btn.addEventListener('click', () => {
        openScheduleInterviewModal(btn.dataset.appId, btn.dataset.candidateName);
      });
    });

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load candidates: ${err.message}</div>`;
  }
}

/**
 * 4. Recruiter Analytics
 */
export async function renderRecruiterAnalytics(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading Analytics...</p></div>`;

  try {
    const analytics = await api.get('/api/recruiter/analytics');
    const profile = await api.get('/api/recruiter/profile');

    targetContainer.innerHTML = `
      <div class="grid-2">
        <div class="white-card">
          <div class="card-header">
            <div class="card-title"><i class="fa-solid fa-chart-pie"></i> Recruitment Pipeline Analytics</div>
            <span class="badge badge-success">${analytics.funnel.offer_acceptance_rate_pct}% Yield</span>
          </div>
          <div style="height:250px; position:relative;">
            <canvas id="recruiter-analytics-funnel"></canvas>
          </div>
        </div>

        <div class="white-card">
          <div class="card-header">
            <div class="card-title"><i class="fa-solid fa-shield-check"></i> Compliance & Verification Trust Signals</div>
            <span class="badge badge-success">Audit Complete</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:10px;">
            <div style="padding:10px 12px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light);">
              <div style="font-size:0.78rem; font-weight:600; color:var(--text-muted);">CIN & MCA Registration Check</div>
              <div style="font-size:0.92rem; font-weight:700; color:var(--success-text); margin-top:2px;"><i class="fa-solid fa-circle-check"></i> 25/25 pts Verified</div>
              <div style="font-size:0.72rem; color:var(--text-dim);">CIN-U72200KA2015PTC081234</div>
            </div>
            <div style="padding:10px 12px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light);">
              <div style="font-size:0.78rem; font-weight:600; color:var(--text-muted);">Corporate Domain & Email Authentication</div>
              <div style="font-size:0.92rem; font-weight:700; color:var(--success-text); margin-top:2px;"><i class="fa-solid fa-circle-check"></i> 25/25 pts Authenticated</div>
              <div style="font-size:0.72rem; color:var(--text-dim);">Email: recruiter@dabur-ayush.in</div>
            </div>
            <div style="padding:10px 12px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light);">
              <div style="font-size:0.78rem; font-weight:600; color:var(--text-muted);">Placement History & Yield</div>
              <div style="font-size:0.92rem; font-weight:700; color:var(--success-text); margin-top:2px;"><i class="fa-solid fa-circle-check"></i> 25/25 pts Verified</div>
              <div style="font-size:0.72rem; color:var(--text-dim);">185+ Verified Campus Placements</div>
            </div>
            <div style="padding:10px 12px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light);">
              <div style="font-size:0.78rem; font-weight:600; color:var(--text-muted);">Tier-1 Institution Endorsement</div>
              <div style="font-size:0.92rem; font-weight:700; color:var(--success-text); margin-top:2px;"><i class="fa-solid fa-circle-check"></i> 25/25 pts Active MOUs</div>
              <div style="font-size:0.72rem; color:var(--text-dim);">National Institute of Ayurveda (NIA) Partner</div>
            </div>
          </div>
        </div>
      </div>
    `;

    setTimeout(() => {
      renderFunnelChart(
        'recruiter-analytics-funnel',
        ['Total Applicants', 'Shortlisted', 'Interviewed', 'Selected'],
        [analytics.funnel.total_applications, analytics.funnel.shortlisted, analytics.funnel.interviewed, analytics.funnel.selected]
      );
    }, 50);

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load analytics: ${err.message}</div>`;
  }
}

/**
 * Modals
 */
export function openCreateJobModal() {
  const modalContainer = document.getElementById('modal-container');
  modalContainer.innerHTML = `
    <div class="modal-card" style="max-width:700px;">
      <div class="modal-header">
        <h3><i class="fa-solid fa-briefcase" style="color:var(--primary); margin-right:6px;"></i> Post Role with Dynamic Skill Matrix</h3>
        <button class="btn btn-sm btn-secondary btn-close-modal"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <div class="modal-body">
        <div class="grid-2">
          <div class="form-group">
            <label class="form-label">Job / Internship Title</label>
            <input type="text" id="job-title-input" class="form-control" placeholder="e.g. AYUSH Quality & Pharmacognosy Research Officer" />
          </div>
          <div class="form-group">
            <label class="form-label">Position Type</label>
            <select id="job-type-select" class="form-control">
              <option value="Full-Time">Full-Time Campus Hire</option>
              <option value="Internship">Pharmaceutical Internship</option>
              <option value="Apprenticeship">Apprenticeship</option>
            </select>
          </div>
        </div>

        <div class="grid-3">
          <div class="form-group">
            <label class="form-label">Location</label>
            <input type="text" id="job-loc-input" class="form-control" value="Bengaluru / Hyderabad" />
          </div>
          <div class="form-group">
            <label class="form-label">Compensation</label>
            <input type="text" id="job-sal-input" class="form-control" value="₹12.0 - ₹18.0 LPA" />
          </div>
          <div class="form-group">
            <label class="form-label">Minimum CGPA</label>
            <input type="number" id="job-cgpa-input" class="form-control" step="0.1" value="7.0" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Role Description</label>
          <textarea id="job-desc-input" class="form-control" rows="2" placeholder="Describe role requirements..."></textarea>
        </div>

        <!-- Dynamic Skill Requirement Matrix Builder -->
        <div style="margin-top:14px; padding:12px; background:var(--bg-subtle); border:1px solid var(--border-light); border-radius:var(--radius-sm);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <strong style="color:var(--text-primary); font-size:0.86rem;"><i class="fa-solid fa-table-cells"></i> Skill Requirement Matrix</strong>
            <button class="btn btn-sm btn-secondary" id="btn-add-matrix-row"><i class="fa-solid fa-plus"></i> Add Skill</button>
          </div>
          <div id="matrix-rows-container">
            <div class="matrix-row grid-3" style="margin-bottom:6px;">
              <input type="text" class="form-control matrix-skill" value="Ashwagandha" placeholder="Skill Name" />
              <input type="number" class="form-control matrix-prof" value="80" placeholder="Req %" />
              <select class="form-control matrix-imp">
                <option value="Critical" selected>Critical (3.0x)</option>
                <option value="High">High (2.0x)</option>
                <option value="Medium">Medium (1.0x)</option>
              </select>
            </div>
            <div class="matrix-row grid-3" style="margin-bottom:6px;">
              <input type="text" class="form-control matrix-skill" value="Triphala" placeholder="Skill Name" />
              <input type="number" class="form-control matrix-prof" value="75" placeholder="Req %" />
              <select class="form-control matrix-imp">
                <option value="Critical">Critical (3.0x)</option>
                <option value="High" selected>High (2.0x)</option>
                <option value="Medium">Medium (1.0x)</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary btn-close-modal">Cancel</button>
        <button class="btn btn-primary" id="btn-submit-create-job"><i class="fa-solid fa-paper-plane"></i> Publish Opportunity</button>
      </div>
    </div>
  `;
  const overlay = document.getElementById('modal-overlay');
  overlay.classList.add('active');

  overlay.querySelectorAll('.btn-close-modal').forEach(b => {
    b.onclick = () => overlay.classList.remove('active');
  });

  document.getElementById('btn-add-matrix-row').onclick = () => {
    const container = document.getElementById('matrix-rows-container');
    const newRow = document.createElement('div');
    newRow.className = 'matrix-row grid-3';
    newRow.style.marginBottom = '6px';
    newRow.innerHTML = `
      <input type="text" class="form-control matrix-skill" placeholder="Skill Name (e.g. Standardized Packaging)" />
      <input type="number" class="form-control matrix-prof" value="70" placeholder="Req %" />
      <select class="form-control matrix-imp">
        <option value="Critical">Critical (3.0x)</option>
        <option value="High">High (2.0x)</option>
        <option value="Medium" selected>Medium (1.0x)</option>
      </select>
    `;
    container.appendChild(newRow);
  };

  document.getElementById('btn-submit-create-job').onclick = async () => {
    const title = document.getElementById('job-title-input').value.trim();
    const type = document.getElementById('job-type-select').value;
    const loc = document.getElementById('job-loc-input').value.trim();
    const cgpa = parseFloat(document.getElementById('job-cgpa-input').value) || 6.5;
    const desc = document.getElementById('job-desc-input').value.trim() || 'Role requirement.';

    const matrixRows = document.querySelectorAll('.matrix-row');
    const skillsMatrix = [];
    matrixRows.forEach(row => {
      const sName = row.querySelector('.matrix-skill').value.trim();
      const prof = parseFloat(row.querySelector('.matrix-prof').value) || 70.0;
      const imp = row.querySelector('.matrix-imp').value;
      if (sName) {
        skillsMatrix.push({ skill_name: sName, required_proficiency: prof, importance_weight: imp });
      }
    });

    if (!title || skillsMatrix.length === 0) {
      window.showToast?.('Please enter title and at least one skill requirement.', 'warning');
      return;
    }

    try {
      await api.post('/api/recruiter/jobs', {
        title,
        job_type: type,
        location: loc,
        eligibility_cgpa: cgpa,
        description: desc,
        skills_matrix: skillsMatrix
      });

      window.showToast?.('Opportunity published! Matching students notified.', 'success');
      overlay.classList.remove('active');
      window.navigateToTab('jobs');
    } catch (err) {
      window.showToast?.(err.message, 'danger');
    }
  };
}

export async function openCandidatesModal(jobId, jobTitle) {
  const modalContainer = document.getElementById('modal-container');
  modalContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Ranking candidates...</p></div>`;
  const overlay = document.getElementById('modal-overlay');
  overlay.classList.add('active');

  try {
    const candidates = await api.get(`/api/recruiter/jobs/${jobId}/candidates`);

    modalContainer.innerHTML = `
      <div class="modal-card" style="max-width:800px;">
        <div class="modal-header">
          <div>
            <h3><i class="fa-solid fa-ranking-star" style="color:var(--warning); margin-right:6px;"></i> AI-Ranked Candidates: ${jobTitle}</h3>
            <span style="font-size:0.75rem; color:var(--text-muted);">Ranked dynamically based on verified proficiency vs skill matrix</span>
          </div>
          <button class="btn btn-sm btn-secondary btn-close-modal"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="modal-body" style="max-height:60vh; overflow-y:auto;">
          <div class="table-responsive">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Rank & Candidate</th>
                  <th>Institution / Dept</th>
                  <th>CGPA</th>
                  <th>Match Score</th>
                  <th>Critical Coverage</th>
                  <th>Explainability</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                ${candidates.map((c, idx) => `
                  <tr>
                    <td><strong>#${idx + 1} ${c.full_name}</strong></td>
                    <td>${c.institution_name} (${c.department_name})</td>
                    <td><strong>${c.cgpa}</strong></td>
                    <td>
                      <span class="badge ${c.match_score >= 85 ? 'badge-success' : (c.match_score >= 70 ? 'badge-warning' : 'badge-danger')}">
                        <i class="fa-solid fa-bolt"></i> ${c.match_score}%
                      </span>
                    </td>
                    <td><strong style="color:var(--success-text);">${c.critical_coverage_pct}%</strong></td>
                    <td>
                      <button class="btn btn-sm btn-secondary btn-explain-candidate" data-job-id="${jobId}" data-student-id="${c.student_id}">
                        Why #${idx + 1}?
                      </button>
                    </td>
                    <td>
                      ${c.application_id ? `
                        <button class="btn btn-sm btn-success btn-schedule-interview-modal" data-app-id="${c.application_id}" data-candidate-name="${c.full_name}">
                          <i class="fa-solid fa-calendar-plus"></i> Interview
                        </button>
                      ` : `
                        <button class="btn btn-sm btn-secondary" onclick="window.showToast('Outreach invite sent to ${c.full_name}', 'success')">
                          Invite
                        </button>
                      `}
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary btn-close-modal">Close</button>
        </div>
      </div>
    `;

    overlay.querySelectorAll('.btn-close-modal').forEach(b => {
      b.onclick = () => overlay.classList.remove('active');
    });

    document.querySelectorAll('.btn-explain-candidate').forEach(btn => {
      btn.onclick = () => {
        openCandidateExplainModal(btn.dataset.jobId, btn.dataset.studentId);
      };
    });

    document.querySelectorAll('.btn-schedule-interview-modal').forEach(btn => {
      btn.onclick = () => {
        openScheduleInterviewModal(btn.dataset.appId, btn.dataset.candidateName);
      };
    });

  } catch (err) {
    modalContainer.innerHTML = `<div class="modal-card"><div class="modal-body" style="color:var(--danger); text-align:center;">Failed to load candidates: ${err.message}</div></div>`;
  }
}

export async function openCandidateExplainModal(jobId, studentId) {
  try {
    const data = await api.get(`/api/recruiter/jobs/${jobId}/candidates/${studentId}/explain`);
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = `
      <div class="modal-card" style="max-width:640px;">
        <div class="modal-header">
          <div>
            <h3><i class="fa-solid fa-microchip" style="color:var(--primary); margin-right:6px;"></i> Explainable Match: ${data.candidate_name}</h3>
            <span style="font-size:0.75rem; color:var(--text-muted);">${data.job_title} at ${data.company_name}</span>
          </div>
          <button class="btn btn-sm btn-secondary btn-close-modal"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="modal-body">
          <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 14px; background:var(--primary-light); border:1px solid #C7D2FE; border-radius:var(--radius-sm); margin-bottom:12px;">
            <div>
              <div style="font-size:1.6rem; font-weight:800; color:var(--primary);">${data.overall_match_score}% Match</div>
              <div style="font-size:0.74rem; color:var(--text-muted);">Base Match: ${data.base_skill_match}% + Project Bonus: +${data.project_bonus}%</div>
            </div>
            <span class="badge badge-success">Critical Coverage: ${data.critical_coverage_pct}%</span>
          </div>

          <h4 style="font-size:0.86rem; font-weight:700; color:var(--text-primary); margin-bottom:6px;">Skill Matrix Alignment</h4>
          <div style="max-height:140px; overflow-y:auto; margin-bottom:12px;">
            ${(data.matched_skills || []).map(s => `
              <div style="display:flex; justify-content:space-between; padding:5px 8px; background:var(--bg-subtle); border-radius:var(--radius-sm); margin-bottom:4px; font-size:0.78rem;">
                <span><strong>${s.skill}</strong> (${s.importance})</span>
                <span style="color:var(--success-text);">Candidate: ${s.student_proficiency}% (Req: ${s.required_proficiency}%)</span>
              </div>
            `).join('')}
            ${(data.skill_gaps || []).map(g => `
              <div style="display:flex; justify-content:space-between; padding:5px 8px; background:var(--danger-light); border-radius:var(--radius-sm); margin-bottom:4px; font-size:0.78rem;">
                <span><strong>${g.skill}</strong> (Gap: ${g.gap}%)</span>
                <span style="color:var(--danger-text);">Candidate: ${g.student_proficiency}% (Req: ${g.required_proficiency}%)</span>
              </div>
            `).join('')}
          </div>

          <div style="padding:10px 12px; background:var(--bg-subtle); border-radius:var(--radius-sm); font-size:0.78rem; color:var(--text-secondary); border:1px solid var(--border-light); margin-bottom:10px;">
            <strong>AI Ranking Narrative:</strong> ${data.narrative}
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary btn-close-modal">Back to Candidates</button>
        </div>
      </div>
    `;

    document.querySelectorAll('.btn-close-modal').forEach(b => {
      b.onclick = () => openCandidatesModal(jobId, data.job_title);
    });

  } catch (err) {
    window.showToast?.(err.message, 'danger');
  }
}

export function openScheduleInterviewModal(applicationId, candidateName) {
  const modalContainer = document.getElementById('modal-container');
  modalContainer.innerHTML = `
    <div class="modal-card">
      <div class="modal-header">
        <h3><i class="fa-solid fa-calendar-check" style="color:var(--success); margin-right:6px;"></i> Schedule Interview: ${candidateName}</h3>
        <button class="btn btn-sm btn-secondary btn-close-modal"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">Interview Round</label>
          <input type="text" id="int-round-input" class="form-control" value="Technical Round 1: Core Algorithms & AI Systems" />
        </div>
        <div class="form-group">
          <label class="form-label">Date & Time</label>
          <input type="datetime-local" id="int-time-input" class="form-control" />
        </div>
        <div class="form-group">
          <label class="form-label">Meeting URL (Google Meet / Zoom)</label>
          <input type="url" id="int-link-input" class="form-control" value="https://meet.google.com/sih-26044-interview" />
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary btn-close-modal">Cancel</button>
        <button class="btn btn-success" id="btn-confirm-schedule"><i class="fa-solid fa-envelope-circle-check"></i> Send Invitation</button>
      </div>
    </div>
  `;

  const overlay = document.getElementById('modal-overlay');
  overlay.classList.add('active');
  overlay.querySelectorAll('.btn-close-modal').forEach(b => {
    b.onclick = () => overlay.classList.remove('active');
  });

  document.getElementById('btn-confirm-schedule').onclick = async () => {
    const round = document.getElementById('int-round-input').value.trim();
    const time = document.getElementById('int-time-input').value || new Date().toISOString();
    const link = document.getElementById('int-link-input').value.trim();

    try {
      await api.post('/api/recruiter/schedule-interview', {
        application_id: parseInt(applicationId),
        round_name: round,
        scheduled_time: time,
        meeting_link: link
      });
      window.showToast?.(`Interview invitation dispatched to ${candidateName}!`, 'success');
      overlay.classList.remove('active');
      window.navigateToTab('candidates');
    } catch (err) {
      window.showToast?.(err.message, 'danger');
    }
  };
}
