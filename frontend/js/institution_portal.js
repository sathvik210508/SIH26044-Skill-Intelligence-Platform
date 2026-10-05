/**
 * SIH26044 — Institution / TPO Portal Module (Clean SaaS Design)
 */

import { api } from './api.js';

/**
 * 1. Institution Dashboard
 */
export async function renderInstitutionDashboard(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading Institution Intelligence...</p></div>`;

  try {
    const dash = await api.get('/api/institution/dashboard');
    const heatmap = await api.get('/api/institution/skill-heatmap');
    const workshops = await api.get('/api/institution/workshops');

    targetContainer.innerHTML = `
      <!-- Institution Header -->
      <div class="white-card" style="border-left:4px solid var(--warning);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
          <div>
            <div style="display:flex; align-items:center; gap:8px;">
              <h2 style="font-size:1.35rem; font-weight:700; color:var(--text-primary);">${dash.name}</h2>
              <span class="badge badge-success">${dash.tier}</span>
              <span class="badge badge-purple">PRS: ${dash.readiness_score}%</span>
            </div>
            <p style="color:var(--text-muted); font-size:0.85rem; margin-top:3px;">
              Code: <strong>${dash.code}</strong> • State: <strong>${dash.state}</strong> • Accreditation: <strong>NAAC A++</strong>
            </p>
          </div>
          <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <button class="btn btn-secondary" id="btn-inst-bulk-modal"><i class="fa-solid fa-user-plus"></i> Bulk Student Generator</button>
            <button class="btn btn-primary" id="btn-inst-workshop-modal"><i class="fa-solid fa-chalkboard-user"></i> Launch Upskilling Program</button>
          </div>
        </div>
      </div>

      <!-- KPI Metrics -->
      <div class="grid-4">
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--primary-light); color:var(--primary);"><i class="fa-solid fa-users"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${dash.kpis.total_students}</div>
            <div class="kpi-label">Enrolled Students</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-circle-check"></i> Across 4 Departments</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--accent-cyan-light); color:var(--accent-cyan);"><i class="fa-solid fa-brain"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${dash.kpis.avg_skill_proficiency}%</div>
            <div class="kpi-label">Avg Verified Proficiency</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-calculator"></i> Evidence Calculated</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--success-light); color:var(--success);"><i class="fa-solid fa-user-graduate"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${dash.kpis.placement_rate_pct}%</div>
            <div class="kpi-label">Placement Rate</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-building"></i> Top Tier Recruiters</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--warning-light); color:var(--warning);"><i class="fa-solid fa-laptop-code"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${dash.kpis.internship_participation_pct}%</div>
            <div class="kpi-label">Internship Rate</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-arrow-trend-up"></i> High Conversion</div>
          </div>
        </div>
      </div>

      <!-- Skill Gap Heatmap (Overview) -->
      <div class="white-card">
        <div class="card-header">
          <div>
            <div class="card-title"><i class="fa-solid fa-fire" style="color:var(--danger);"></i> Institutional Skill Deficit Heatmap</div>
            <p style="color:var(--text-muted); font-size:0.78rem; margin-top:2px;">
              Multi-Year skill proficiency matrix. Red indicates deficit below 50% requiring training intervention.
            </p>
          </div>
          <span class="badge badge-danger">Critical Deficit: ${heatmap.highest_gap_skill}</span>
        </div>
        <div class="table-responsive">
          <table class="custom-table heatmap-table">
            <thead>
              <tr>
                <th style="text-align:left;">Technical Skill</th>
                <th>2nd Year Batch</th>
                <th>3rd Year Batch</th>
                <th>4th Year Batch</th>
                <th>Institutional Average</th>
                <th>Action Recommendation</th>
              </tr>
            </thead>
            <tbody>
              ${heatmap.heatmap_matrix.map(row => `
                <tr>
                  <td style="text-align:left;"><strong>${row.skill}</strong></td>
                  <td><div class="heatmap-cell ${row.year_2 >= 70 ? 'cell-high' : (row.year_2 >= 50 ? 'cell-med' : 'cell-low')}">${row.year_2}%</div></td>
                  <td><div class="heatmap-cell ${row.year_3 >= 70 ? 'cell-high' : (row.year_3 >= 50 ? 'cell-med' : 'cell-low')}">${row.year_3}%</div></td>
                  <td><div class="heatmap-cell ${row.year_4 >= 70 ? 'cell-high' : (row.year_4 >= 50 ? 'cell-med' : 'cell-low')}">${row.year_4}%</div></td>
                  <td><strong>${row.avg}%</strong></td>
                  <td>
                    ${row.avg < 55 ? `
                      <button class="btn btn-sm btn-primary btn-auto-workshop" data-skill="${row.skill}" style="font-size:0.75rem;">
                        <i class="fa-solid fa-wand-magic-sparkles"></i> Launch Workshop
                      </button>
                    ` : `<span style="font-size:0.78rem; color:var(--success-text);"><i class="fa-solid fa-check"></i> Satisfactory</span>`}
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Targeted Workshops Delta -->
      <div class="white-card">
        <div class="card-header">
          <div class="card-title"><i class="fa-solid fa-chalkboard-user"></i> Active Upskilling Programs & Measured Impact</div>
          <span class="badge badge-success">+25.7% Avg Measured Improvement</span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap:14px;">
          ${workshops.map(w => `
            <div style="padding:14px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light);">
              <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <span class="badge ${w.status === 'Completed' ? 'badge-success' : 'badge-info'}">${w.status}</span>
                <span style="font-size:0.75rem; color:var(--text-muted);"><i class="fa-solid fa-users"></i> ${w.registered_count} Enrolled</span>
              </div>
              <h4 style="font-size:0.98rem; font-weight:700; margin-top:8px; color:var(--text-primary);">${w.title}</h4>
              <p style="font-size:0.78rem; color:var(--text-muted); margin-top:2px;">
                Target: <strong>${w.target_skill_name}</strong> • ${w.target_department} (Yr ${w.target_year})
              </p>
              <div style="margin-top:10px; padding:8px 10px; background:#FFFFFF; border-radius:var(--radius-sm); border:1px solid var(--border-light);">
                <div style="display:flex; justify-content:space-between; font-size:0.76rem; color:var(--text-muted);">
                  <span>Pre: <strong>${w.pre_avg_score}%</strong></span>
                  <span>Post: <strong>${w.post_avg_score}%</strong></span>
                </div>
                <div style="margin-top:4px; font-weight:700; color:var(--success-text); font-size:0.86rem;">
                  Measured Delta: +${w.improvement_delta} percentage points
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    document.getElementById('btn-inst-bulk-modal')?.addEventListener('click', () => openBulkCreateModal());
    document.getElementById('btn-inst-workshop-modal')?.addEventListener('click', () => openCreateWorkshopModal());

    document.querySelectorAll('.btn-auto-workshop').forEach(btn => {
      btn.addEventListener('click', () => {
        openCreateWorkshopModal(btn.dataset.skill);
      });
    });

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load institution dashboard: ${err.message}</div>`;
  }
}

/**
 * 2. Institution Student Roster
 */
export async function renderStudentRosterView(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading Student Roster...</p></div>`;

  try {
    const students = await api.get('/api/institution/students');

    targetContainer.innerHTML = `
      <div class="white-card">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
          <div>
            <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">Student Roster & Skill Telemetry</h3>
            <p style="color:var(--text-muted); font-size:0.82rem; margin-top:2px;">
              Manage student academic records, verified skill scores, and batch accounts.
            </p>
          </div>
          <button class="btn btn-primary" id="btn-roster-bulk-create"><i class="fa-solid fa-user-plus"></i> Bulk Student Generator</button>
        </div>
      </div>

      <div class="white-card">
        <div class="card-header">
          <div class="card-title"><i class="fa-solid fa-users"></i> Enrolled Students (${students.length})</div>
          <span class="badge badge-info">Chaitanya Bharathi Institute of Technology</span>
        </div>
        <div class="table-responsive">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Roll No</th>
                <th>Student Name</th>
                <th>Department & Year</th>
                <th>CGPA</th>
                <th>Avg Proficiency</th>
                <th>Top Verified Skills</th>
                <th>Placement Status</th>
              </tr>
            </thead>
            <tbody>
              ${students.map(s => `
                <tr>
                  <td><span class="badge badge-purple">${s.roll_number}</span></td>
                  <td><strong>${s.full_name}</strong></td>
                  <td>${s.department} (Yr ${s.current_year})</td>
                  <td><strong>${s.cgpa}</strong></td>
                  <td>
                    <span class="badge ${s.avg_proficiency >= 75 ? 'badge-success' : (s.avg_proficiency >= 50 ? 'badge-warning' : 'badge-danger')}">
                      ${s.avg_proficiency}%
                    </span>
                  </td>
                  <td><span style="font-size:0.78rem; color:var(--text-secondary);">${s.top_skills.join(', ')}</span></td>
                  <td><span class="badge badge-info">${s.placement_status}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;

    document.getElementById('btn-roster-bulk-create')?.addEventListener('click', () => openBulkCreateModal());

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load student roster: ${err.message}</div>`;
  }
}

/**
 * 3. Institution Skill Gap Heatmap
 */
export async function renderInstitutionHeatmapView(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading Skill Deficit Heatmap...</p></div>`;

  try {
    const heatmap = await api.get('/api/institution/skill-heatmap');

    targetContainer.innerHTML = `
      <div class="white-card">
        <div class="card-header">
          <div>
            <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">Institution-Wide Skill Deficit Heatmap</h3>
            <p style="color:var(--text-muted); font-size:0.82rem; margin-top:2px;">
              Multi-Year skill competency breakdown across Computer Science, AI, and IT batches.
            </p>
          </div>
          <button class="btn btn-primary btn-sm" id="btn-heatmap-create-ws"><i class="fa-solid fa-plus"></i> Launch Workshop</button>
        </div>
        <div class="table-responsive">
          <table class="custom-table heatmap-table">
            <thead>
              <tr>
                <th style="text-align:left;">Technical Skill</th>
                <th>2nd Year Batch</th>
                <th>3rd Year Batch</th>
                <th>4th Year Batch</th>
                <th>Institutional Average</th>
                <th>Action Recommendation</th>
              </tr>
            </thead>
            <tbody>
              ${heatmap.heatmap_matrix.map(row => `
                <tr>
                  <td style="text-align:left;"><strong>${row.skill}</strong></td>
                  <td><div class="heatmap-cell ${row.year_2 >= 70 ? 'cell-high' : (row.year_2 >= 50 ? 'cell-med' : 'cell-low')}">${row.year_2}%</div></td>
                  <td><div class="heatmap-cell ${row.year_3 >= 70 ? 'cell-high' : (row.year_3 >= 50 ? 'cell-med' : 'cell-low')}">${row.year_3}%</div></td>
                  <td><div class="heatmap-cell ${row.year_4 >= 70 ? 'cell-high' : (row.year_4 >= 50 ? 'cell-med' : 'cell-low')}">${row.year_4}%</div></td>
                  <td><strong>${row.avg}%</strong></td>
                  <td>
                    ${row.avg < 55 ? `
                      <button class="btn btn-sm btn-primary btn-auto-workshop" data-skill="${row.skill}">
                        <i class="fa-solid fa-wand-magic-sparkles"></i> Launch Workshop
                      </button>
                    ` : `<span style="font-size:0.78rem; color:var(--success-text);"><i class="fa-solid fa-check"></i> Satisfactory</span>`}
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;

    document.getElementById('btn-heatmap-create-ws')?.addEventListener('click', () => openCreateWorkshopModal());

    document.querySelectorAll('.btn-auto-workshop').forEach(btn => {
      btn.addEventListener('click', () => {
        openCreateWorkshopModal(btn.dataset.skill);
      });
    });

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load heatmap: ${err.message}</div>`;
  }
}

/**
 * 4. Placement Readiness View
 */
export async function renderPlacementIntelligenceView(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading Placement Intelligence...</p></div>`;

  try {
    const data = await api.get('/api/institution/placement-intelligence');

    targetContainer.innerHTML = `
      <div class="grid-4">
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--success-light); color:var(--success);"><i class="fa-solid fa-user-check"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${data.overall_placement_pct}%</div>
            <div class="kpi-label">Placement Rate</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-arrow-trend-up"></i> +5.2% YoY</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--primary-light); color:var(--primary);"><i class="fa-solid fa-handshake"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${data.internship_to_fulltime_conversion_pct}%</div>
            <div class="kpi-label">PPO Conversion</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-check"></i> Industry High</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--accent-cyan-light); color:var(--accent-cyan);"><i class="fa-solid fa-indian-rupee-sign"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">₹${data.avg_package_lpa} LPA</div>
            <div class="kpi-label">Average Package</div>
            <div class="kpi-sub positive">Highest: ₹${data.highest_package_lpa} LPA</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--warning-light); color:var(--warning);"><i class="fa-solid fa-building"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${data.company_distribution.length}</div>
            <div class="kpi-label">Enterprise Partners</div>
            <div class="kpi-sub positive">Tier-1 Corporates</div>
          </div>
        </div>
      </div>

      <div class="grid-2">
        <div class="white-card">
          <div class="card-header">
            <div class="card-title"><i class="fa-solid fa-building"></i> Top Hiring Companies</div>
          </div>
          <div class="table-responsive">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Offers Extended</th>
                  <th>Avg Package</th>
                </tr>
              </thead>
              <tbody>
                ${data.company_distribution.map(c => `
                  <tr>
                    <td><strong>${c.company}</strong></td>
                    <td><span class="badge badge-success">${c.offers} Offers</span></td>
                    <td><strong>₹${c.avg_package} LPA</strong></td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>

        <div class="white-card">
          <div class="card-header">
            <div class="card-title"><i class="fa-solid fa-graduation-cap"></i> Department Placement Rates</div>
          </div>
          <div class="table-responsive">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Department</th>
                  <th>Placement Rate</th>
                </tr>
              </thead>
              <tbody>
                ${data.department_placement_rates.map(d => `
                  <tr>
                    <td><strong>${d.department}</strong></td>
                    <td>
                      <div style="display:flex; align-items:center; gap:8px;">
                        <span class="badge badge-success">${d.rate}%</span>
                        <div class="progress-bar-container" style="flex:1;">
                          <div class="progress-bar-fill success" style="width:${d.rate}%;"></div>
                        </div>
                      </div>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    `;

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load placement intelligence: ${err.message}</div>`;
  }
}

/**
 * 5. Targeted Workshops View
 */
export async function renderWorkshopsView(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading Workshops...</p></div>`;

  try {
    const workshops = await api.get('/api/institution/workshops');

    targetContainer.innerHTML = `
      <div class="white-card">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
          <div>
            <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">Targeted Upskilling Workshops</h3>
            <p style="color:var(--text-muted); font-size:0.82rem; margin-top:2px;">
              Conduct targeted bootcamps for student cohorts with measured pre vs post training effectiveness.
            </p>
          </div>
          <button class="btn btn-primary" id="btn-create-ws-page"><i class="fa-solid fa-plus"></i> Create Workshop</button>
        </div>
      </div>

      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(340px, 1fr)); gap:16px;">
        ${workshops.map(w => `
          <div class="white-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
              <span class="badge ${w.status === 'Completed' ? 'badge-success' : 'badge-info'}">${w.status}</span>
              <span style="font-size:0.75rem; color:var(--text-muted);"><i class="fa-solid fa-users"></i> ${w.registered_count} Students</span>
            </div>
            <h4 style="font-size:1.05rem; font-weight:700; margin-top:8px; color:var(--text-primary);">${w.title}</h4>
            <p style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">
              Target: <strong>${w.target_skill_name}</strong> • ${w.target_department} (Yr ${w.target_year})
            </p>
            <div style="margin-top:12px; padding:10px 12px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light);">
              <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:var(--text-muted);">
                <span>Pre-Training: <strong>${w.pre_avg_score}%</strong></span>
                <span>Post-Training: <strong>${w.post_avg_score}%</strong></span>
              </div>
              <div style="margin-top:4px; font-weight:700; color:var(--success-text); font-size:0.88rem;">
                Measured Improvement: +${w.improvement_delta} percentage points
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    `;

    document.getElementById('btn-create-ws-page')?.addEventListener('click', () => openCreateWorkshopModal());

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load workshops: ${err.message}</div>`;
  }
}

/**
 * Modals
 */
export function openBulkCreateModal() {
  const modalContainer = document.getElementById('modal-container');
  modalContainer.innerHTML = `
    <div class="modal-card">
      <div class="modal-header">
        <h3><i class="fa-solid fa-users-gear" style="color:var(--primary); margin-right:6px;"></i> Bulk Student Account Generator</h3>
        <button class="btn btn-sm btn-secondary btn-close-modal"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <div class="modal-body">
        <p style="color:var(--text-muted); font-size:0.84rem; margin-bottom:14px;">
          Batch-create realistic student profiles with academic indicators, verified curriculum records, and baseline skills.
        </p>
        <div class="form-group">
          <label class="form-label">Department</label>
          <select id="bulk-dept-select" class="form-control">
            <option value="Dravyaguna Vijnana (Herbal Pharmacology)">Dravyaguna Vijnana (Herbal Pharmacology)</option>
            <option value="Rasa Shastra & Bhaishajya Kalpana">Rasa Shastra & Bhaishajya Kalpana</option>
            <option value="Ayurvedic Quality Control & Drug Standardization">Ayurvedic Quality Control & Drug Standardization</option>
            <option value="Agada Tantra & Pharmacovigilance">Agada Tantra & Pharmacovigilance</option>
          </select>
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label class="form-label">Academic Year</label>
            <select id="bulk-year-select" class="form-control">
              <option value="2">2nd Year (Sophomore)</option>
              <option value="3">3rd Year (Pre-Final)</option>
              <option value="4">4th Year (Final Year)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Count</label>
            <input type="number" id="bulk-count-input" class="form-control" value="15" min="5" max="50" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Roll Number Prefix</label>
          <input type="text" id="bulk-prefix-input" class="form-control" value="24NIA" />
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary btn-close-modal">Cancel</button>
        <button class="btn btn-primary" id="btn-confirm-bulk-create"><i class="fa-solid fa-check"></i> Generate Accounts</button>
      </div>
    </div>
  `;
  const overlay = document.getElementById('modal-overlay');
  overlay.classList.add('active');
  overlay.querySelectorAll('.btn-close-modal').forEach(b => {
    b.onclick = () => overlay.classList.remove('active');
  });

  document.getElementById('btn-confirm-bulk-create').onclick = async () => {
    const dept = document.getElementById('bulk-dept-select').value;
    const year = parseInt(document.getElementById('bulk-year-select').value);
    const count = parseInt(document.getElementById('bulk-count-input').value) || 15;
    const prefix = document.getElementById('bulk-prefix-input').value.trim() || '24NIA';

    try {
      const res = await api.post('/api/institution/bulk-create-students', {
        department_name: dept,
        current_year: year,
        count: count,
        roll_prefix: prefix
      });
      window.showToast?.(`Generated ${res.created_count} student accounts for ${dept}!`, 'success');
      overlay.classList.remove('active');
      window.navigateToTab('students');
    } catch (err) {
      window.showToast?.(err.message, 'danger');
    }
  };
}

export function openCreateWorkshopModal(presetSkill = "AYUSH Good Manufacturing Practice (GMP)") {
  const modalContainer = document.getElementById('modal-container');
  modalContainer.innerHTML = `
    <div class="modal-card">
      <div class="modal-header">
        <h3><i class="fa-solid fa-chalkboard-user" style="color:var(--primary); margin-right:6px;"></i> Launch Targeted Upskilling Workshop</h3>
        <button class="btn btn-sm btn-secondary btn-close-modal"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">Workshop Title</label>
          <input type="text" id="ws-title-input" class="form-control" value="Intensive ${presetSkill} & Quality Standardization Bootcamp" />
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label class="form-label">Target Skill Deficit</label>
            <input type="text" id="ws-skill-input" class="form-control" value="${presetSkill}" />
          </div>
          <div class="form-group">
            <label class="form-label">Proficiency Cutoff (Threshold)</label>
            <input type="number" id="ws-cutoff-input" class="form-control" value="50" placeholder="e.g. < 50%" />
          </div>
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label class="form-label">Department</label>
            <select id="ws-dept-select" class="form-control">
              <option value="Dravyaguna Vijnana (Herbal Pharmacology)">Dravyaguna Vijnana (Herbal Pharmacology)</option>
              <option value="Rasa Shastra & Bhaishajya Kalpana">Rasa Shastra & Bhaishajya Kalpana</option>
              <option value="All Departments">All Departments</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Target Year</label>
            <select id="ws-year-select" class="form-control">
              <option value="2">2nd Year Students</option>
              <option value="3">3rd Year Students</option>
              <option value="4">4th Year Students</option>
            </select>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary btn-close-modal">Cancel</button>
        <button class="btn btn-success" id="btn-confirm-create-ws"><i class="fa-solid fa-bullhorn"></i> Launch & Notify Students</button>
      </div>
    </div>
  `;
  const overlay = document.getElementById('modal-overlay');
  overlay.classList.add('active');
  overlay.querySelectorAll('.btn-close-modal').forEach(b => {
    b.onclick = () => overlay.classList.remove('active');
  });

  document.getElementById('btn-confirm-create-ws').onclick = async () => {
    const title = document.getElementById('ws-title-input').value.trim();
    const skill = document.getElementById('ws-skill-input').value.trim();
    const cutoff = parseFloat(document.getElementById('ws-cutoff-input').value) || 50.0;
    const dept = document.getElementById('ws-dept-select').value;
    const year = parseInt(document.getElementById('ws-year-select').value);

    try {
      await api.post('/api/institution/workshops', {
        title: title,
        description: `Hands-on training targeted at students with ${skill} proficiency below ${cutoff}%.`,
        target_skill_name: skill,
        target_department: dept,
        target_year: year,
        target_proficiency_max: cutoff
      });
      window.showToast?.(`Workshop launched! Eligible students have been notified.`, 'success');
      overlay.classList.remove('active');
      window.navigateToTab('workshops');
    } catch (err) {
      window.showToast?.(err.message, 'danger');
    }
  };
}
