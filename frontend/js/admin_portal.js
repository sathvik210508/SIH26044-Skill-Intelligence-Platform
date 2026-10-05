/**
 * SIH26044 — Admin / Ministry Portal Module (Clean SaaS Design)
 */

import { api } from './api.js';
import { renderSupplyDemandBar } from './charts.js';

/**
 * 1. Admin National Dashboard
 */
export async function renderAdminDashboard(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Aggregating National Skill Ecosystem Telemetry...</p></div>`;

  try {
    const dash = await api.get('/api/admin/national-dashboard');
    const supplyDemand = await api.get('/api/admin/supply-demand');
    const readiness = await api.get('/api/admin/readiness-scores');

    const sdLabels = supplyDemand.supply_demand_table.map(s => s.skill);
    const supplyVals = supplyDemand.supply_demand_table.map(s => s.student_supply);
    const demandVals = supplyDemand.supply_demand_table.map(s => s.industry_demand);

    targetContainer.innerHTML = `
      <!-- National Dashboard Banner -->
      <div class="white-card" style="border-left:4px solid var(--danger);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
          <div>
            <div style="display:flex; align-items:center; gap:8px;">
              <h2 style="font-size:1.35rem; font-weight:700; color:var(--text-primary);">National Skill Intelligence Dashboard</h2>
              <span class="badge badge-danger">Ministry Level</span>
            </div>
            <p style="color:var(--text-muted); font-size:0.85rem; margin-top:3px;">
              Real-time closed-loop telemetry across <strong>${dash.ecosystem_summary.total_institutions} Institutions</strong>, <strong>${dash.ecosystem_summary.total_companies_active} Enterprise Partners</strong>, and <strong>${dash.ecosystem_summary.total_students} Students</strong>.
            </p>
          </div>
          <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <button class="btn btn-secondary" id="btn-admin-gov-opp"><i class="fa-solid fa-landmark"></i> Publish Govt Scheme</button>
            <button class="btn btn-primary" id="btn-admin-hackathon"><i class="fa-solid fa-trophy"></i> Launch National Hackathon</button>
          </div>
        </div>
      </div>

      <!-- KPI Metrics -->
      <div class="grid-4">
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--primary-light); color:var(--primary);"><i class="fa-solid fa-certificate"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${dash.ecosystem_summary.total_skills_verified}</div>
            <div class="kpi-label">Verified Skill Records</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-shield-check"></i> Evidence Validated</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--accent-cyan-light); color:var(--accent-cyan);"><i class="fa-solid fa-gauge-high"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${dash.ecosystem_summary.national_readiness_index}%</div>
            <div class="kpi-label">National Readiness</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-chart-line"></i> +4.2% YoY</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--danger-light); color:var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${supplyDemand.critical_national_gaps.length}</div>
            <div class="kpi-label">National Deficits</div>
            <div class="kpi-sub danger"><i class="fa-solid fa-arrow-trend-up"></i> AYUSH GMP & Formulation</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:var(--success-light); color:var(--success);"><i class="fa-solid fa-briefcase"></i></div>
          <div class="kpi-content">
            <div class="kpi-value">${dash.ecosystem_summary.total_opportunities_posted}</div>
            <div class="kpi-label">Active Opportunities</div>
            <div class="kpi-sub positive"><i class="fa-solid fa-building"></i> Multi-state</div>
          </div>
        </div>
      </div>

      <!-- Supply vs Demand Chart & Automated Policy Interventions -->
      <div class="grid-1-2">
        <div class="white-card">
          <div class="card-header">
            <div class="card-title"><i class="fa-solid fa-scale-balanced"></i> National Supply vs Industry Demand</div>
            <span class="badge badge-info">Closed-Loop</span>
          </div>
          <div style="height:260px; position:relative;">
            <canvas id="admin-supply-demand-chart"></canvas>
          </div>
        </div>

        <div class="white-card">
          <div class="card-header">
            <div class="card-title"><i class="fa-solid fa-lightbulb" style="color:var(--warning);"></i> Automated Policy Interventions</div>
            <span class="badge badge-purple">AI Recommended</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:10px;">
            ${supplyDemand.policy_recommendations.map(r => `
              <div style="padding:10px 12px; background:var(--bg-subtle); border-left:3px solid var(--primary); border-radius:var(--radius-sm); font-size:0.82rem; color:var(--text-secondary);">
                <i class="fa-solid fa-bolt" style="color:var(--warning); margin-right:4px;"></i> ${r}
              </div>
            `).join('')}
            <div style="margin-top:4px; font-size:0.75rem; color:var(--text-muted);">
              Recommendations are dynamically generated when national skill deficit exceeds 20%.
            </div>
          </div>
        </div>
      </div>
    `;

    setTimeout(() => {
      renderSupplyDemandBar('admin-supply-demand-chart', sdLabels.slice(0, 6), supplyVals.slice(0, 6), demandVals.slice(0, 6));
    }, 50);

    document.getElementById('btn-admin-gov-opp')?.addEventListener('click', () => openCreateGovOppModal());
    document.getElementById('btn-admin-hackathon')?.addEventListener('click', () => openCreateHackathonModal());

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load national dashboard: ${err.message}</div>`;
  }
}

/**
 * 2. Institutions Platform Readiness Score (PRS) Leaderboard
 */
export async function renderInstitutionsPRSView(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading Institution Leaderboard...</p></div>`;

  try {
    const readiness = await api.get('/api/admin/readiness-scores');

    targetContainer.innerHTML = `
      <div class="white-card">
        <div class="card-header">
          <div>
            <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">Institution Platform Readiness Score (PRS) Leaderboard</h3>
            <p style="color:var(--text-muted); font-size:0.82rem; margin-top:2px;">
              Formula: <strong>PRS = 0.35(S) + 0.25(P) + 0.20(I) + 0.10(T) + 0.10(A)</strong>
            </p>
          </div>
          <span class="badge badge-info">${readiness.length} Accredited Institutions</span>
        </div>
        <div class="table-responsive">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Rank & Institution</th>
                <th>State</th>
                <th>Tier</th>
                <th>Readiness Score</th>
                <th>Readiness Tier</th>
                <th>Formula Breakdown</th>
              </tr>
            </thead>
            <tbody>
              ${readiness.map((inst, idx) => `
                <tr>
                  <td><strong>#${idx + 1} ${inst.institution_name}</strong></td>
                  <td>${inst.state}</td>
                  <td><span class="badge badge-purple">${inst.tier}</span></td>
                  <td>
                    <span class="badge ${inst.platform_readiness_score >= 80 ? 'badge-success' : 'badge-warning'}">
                      <i class="fa-solid fa-gauge-high"></i> ${inst.platform_readiness_score}%
                    </span>
                  </td>
                  <td><strong style="color:${inst.platform_readiness_score >= 80 ? 'var(--success-text)' : 'var(--warning-text)'}; font-size:0.82rem;">${inst.readiness_tier}</strong></td>
                  <td>
                    <span style="font-size:0.75rem; color:var(--text-muted);">
                      S: ${inst.formula_breakdown.S_skill_proficiency.contribution}% | P: ${inst.formula_breakdown.P_placement_rate.contribution}% | I: ${inst.formula_breakdown.I_internship_rate.contribution}%
                    </span>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load leaderboard: ${err.message}</div>`;
  }
}

/**
 * 3. Company Verification & Trust Shield
 */
export async function renderCompanyVerificationView(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading Company Verification Registry...</p></div>`;

  try {
    const companies = await api.get('/api/admin/companies');

    targetContainer.innerHTML = `
      <div class="white-card">
        <div class="card-header">
          <div>
            <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">Enterprise & Recruiter Verification Management</h3>
            <p style="color:var(--text-muted); font-size:0.82rem; margin-top:2px;">
              Multi-signal authenticity evaluation: CIN, corporate domain, placement history, and scam protection.
            </p>
          </div>
          <span class="badge badge-info">${companies.length} Registered Employers</span>
        </div>
        <div class="table-responsive">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Company Name</th>
                <th>CIN / Registration</th>
                <th>Website</th>
                <th>Trust Score</th>
                <th>Verification Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${companies.map(c => `
                <tr>
                  <td><strong>${c.name}</strong><br /><span style="font-size:0.75rem; color:var(--text-muted);">${c.industry}</span></td>
                  <td><code>${c.registration_number}</code></td>
                  <td><a href="${c.website}" target="_blank" style="color:var(--primary); text-decoration:none;">${c.website}</a></td>
                  <td><strong>${c.verification_score}%</strong></td>
                  <td>
                    <span class="badge ${c.verification_status === 'Verified' ? 'badge-success' : (c.verification_status === 'Verification Required' ? 'badge-warning' : 'badge-danger')}">
                      ${c.status_label}
                    </span>
                  </td>
                  <td>
                    <select class="form-control select-company-status" data-company-id="${c.id}" style="width:auto; padding:4px 8px; font-size:0.75rem;">
                      <option value="Verified" ${c.verification_status === 'Verified' ? 'selected' : ''}>🟢 Verified</option>
                      <option value="Verification Required" ${c.verification_status === 'Verification Required' ? 'selected' : ''}>🟡 Verification Required</option>
                      <option value="Suspicious" ${c.verification_status === 'Suspicious' ? 'selected' : ''}>🔴 Flag / Suspicious</option>
                    </select>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;

    document.querySelectorAll('.select-company-status').forEach(sel => {
      sel.onchange = async () => {
        const cId = parseInt(sel.dataset.companyId);
        const newStatus = sel.value;
        try {
          await api.post('/api/admin/companies/verify', { company_id: cId, verification_status: newStatus });
          window.showToast?.(`Updated ${cId} verification status to ${newStatus}!`, 'success');
        } catch (err) {
          window.showToast?.(err.message, 'danger');
        }
      };
    });

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load companies: ${err.message}</div>`;
  }
}

/**
 * 4. National Supply vs Demand
 */
export async function renderSupplyDemandView(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading Supply vs Demand Intelligence...</p></div>`;

  try {
    const supplyDemand = await api.get('/api/admin/supply-demand');

    const sdLabels = supplyDemand.supply_demand_table.map(s => s.skill);
    const supplyVals = supplyDemand.supply_demand_table.map(s => s.student_supply);
    const demandVals = supplyDemand.supply_demand_table.map(s => s.industry_demand);

    targetContainer.innerHTML = `
      <div class="white-card">
        <div class="card-header">
          <div>
            <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">National Skill Supply vs Industry Demand Analysis</h3>
            <p style="color:var(--text-muted); font-size:0.82rem; margin-top:2px;">
              Aggregate talent pipeline availability vs live recruiter job demand across technical competencies.
            </p>
          </div>
          <span class="badge badge-info">National Telemetry</span>
        </div>
        <div style="height:280px; position:relative;">
          <canvas id="admin-supply-demand-page-chart"></canvas>
        </div>
      </div>

      <div class="white-card">
        <div class="card-header">
          <div class="card-title"><i class="fa-solid fa-table-list"></i> Skill Balance Matrix</div>
        </div>
        <div class="table-responsive">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Skill Name</th>
                <th>Student Supply %</th>
                <th>Industry Demand %</th>
                <th>Net Deficit / Surplus</th>
                <th>Trend</th>
                <th>Priority</th>
              </tr>
            </thead>
            <tbody>
              ${supplyDemand.supply_demand_table.map(row => `
                <tr>
                  <td><strong>${row.skill}</strong></td>
                  <td>${row.student_supply}%</td>
                  <td>${row.industry_demand}%</td>
                  <td>
                    <span class="badge ${row.gap_score > 20 ? 'badge-danger' : (row.gap_score > 0 ? 'badge-warning' : 'badge-success')}">
                      ${row.gap_score > 0 ? `-${row.gap_score}% Deficit` : `+${Math.abs(row.gap_score)}% Surplus`}
                    </span>
                  </td>
                  <td><strong>${row.growth_trend}</strong></td>
                  <td><span class="badge ${row.future_priority === 'Critical' ? 'badge-danger' : 'badge-purple'}">${row.future_priority}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;

    setTimeout(() => {
      renderSupplyDemandBar('admin-supply-demand-page-chart', sdLabels, supplyVals, demandVals);
    }, 50);

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load supply/demand: ${err.message}</div>`;
  }
}

/**
 * 5. Hackathons & Government Schemes
 */
export async function renderHackathonsAndSchemesView(targetContainer) {
  targetContainer.innerHTML = `<div style="text-align:center; padding: 40px;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary);"></i><p style="margin-top:10px; color:var(--text-muted);">Loading National Programs...</p></div>`;

  try {
    targetContainer.innerHTML = `
      <div class="white-card">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
          <div>
            <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">National Programs, Hackathons & Government Schemes</h3>
            <p style="color:var(--text-muted); font-size:0.82rem; margin-top:2px;">
              Launch nationwide innovation challenges (SIH model) and publish subsidized apprenticeship programs.
            </p>
          </div>
          <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <button class="btn btn-secondary" id="btn-create-scheme-pg"><i class="fa-solid fa-landmark"></i> Publish Scheme</button>
            <button class="btn btn-primary" id="btn-create-hack-pg"><i class="fa-solid fa-trophy"></i> Announce Hackathon</button>
          </div>
        </div>
      </div>

      <div class="grid-2">
        <div class="white-card">
          <div class="card-header">
            <div class="card-title"><i class="fa-solid fa-trophy" style="color:var(--warning);"></i> Active National Hackathons</div>
            <span class="badge badge-success">SIH 2026</span>
          </div>
          <div style="padding:14px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <strong style="font-size:0.95rem; color:var(--text-primary);">Smart India AYUSH Challenge 2026 (SIH26044)</strong>
              <span class="badge badge-purple">Grand Finale</span>
            </div>
            <p style="font-size:0.8rem; color:var(--text-secondary); margin-top:4px;">Theme: AI-Powered AYUSH Medicine Quality Intelligence & Supply Matching Platform</p>
            <div style="margin-top:8px; font-size:0.78rem; color:var(--text-muted);">
              <strong>Prize Pool:</strong> ₹1,50,000 + Recruiter Fast-Track • <strong>Status:</strong> Active
            </div>
          </div>
        </div>

        <div class="white-card">
          <div class="card-header">
            <div class="card-title"><i class="fa-solid fa-landmark"></i> Central / State Government Schemes</div>
            <span class="badge badge-info">Ministry of AYUSH / CCRAS</span>
          </div>
          <div style="padding:14px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-light);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <strong style="font-size:0.95rem; color:var(--text-primary);">National AYUSH Phytochemical & Quality Apprenticeship</strong>
              <span class="badge badge-success">Govt Funded</span>
            </div>
            <p style="font-size:0.8rem; color:var(--text-secondary); margin-top:4px;">Stipend: ₹16,000 / month + Digital Credential</p>
            <div style="margin-top:8px; font-size:0.78rem; color:var(--text-muted);">
              <strong>Agency:</strong> Ministry of AYUSH / CCRAS
            </div>
          </div>
        </div>
      </div>
    `;

    document.getElementById('btn-create-scheme-pg')?.addEventListener('click', () => openCreateGovOppModal());
    document.getElementById('btn-create-hack-pg')?.addEventListener('click', () => openCreateHackathonModal());

  } catch (err) {
    targetContainer.innerHTML = `<div class="white-card" style="color:var(--danger); padding:30px; text-align:center;">Failed to load programs: ${err.message}</div>`;
  }
}

/**
 * Modals
 */
export function openCreateGovOppModal() {
  const modalContainer = document.getElementById('modal-container');
  modalContainer.innerHTML = `
    <div class="modal-card">
      <div class="modal-header">
        <h3><i class="fa-solid fa-landmark" style="color:var(--primary); margin-right:6px;"></i> Publish Government Scheme / Apprenticeship</h3>
        <button class="btn btn-sm btn-secondary btn-close-modal"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">Scheme / Program Title</label>
          <input type="text" id="gov-title-input" class="form-control" value="National AI & Digital Infrastructure Apprenticeship" />
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label class="form-label">Issuing Ministry / Agency</label>
            <input type="text" id="gov-agency-input" class="form-control" value="Ministry of Electronics & IT / AICTE" />
          </div>
          <div class="form-group">
            <label class="form-label">Stipend / Support</label>
            <input type="text" id="gov-stipend-input" class="form-control" value="₹16,000 / month + Credential" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Application Portal URL</label>
          <input type="url" id="gov-url-input" class="form-control" value="https://internship.aicte-india.org" />
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary btn-close-modal">Cancel</button>
        <button class="btn btn-primary" id="btn-confirm-gov-opp"><i class="fa-solid fa-paper-plane"></i> Publish Scheme</button>
      </div>
    </div>
  `;
  const overlay = document.getElementById('modal-overlay');
  overlay.classList.add('active');
  overlay.querySelectorAll('.btn-close-modal').forEach(b => {
    b.onclick = () => overlay.classList.remove('active');
  });

  document.getElementById('btn-confirm-gov-opp').onclick = async () => {
    const title = document.getElementById('gov-title-input').value.trim();
    const agency = document.getElementById('gov-agency-input').value.trim();
    const stipend = document.getElementById('gov-stipend-input').value.trim();
    const url = document.getElementById('gov-url-input').value.trim();

    try {
      await api.post('/api/admin/government-opportunities', {
        title: title,
        agency: agency,
        stipend_or_pay: stipend,
        application_url: url,
        skills: ["Ashwagandha", "AYUSH Good Manufacturing Practice (GMP)", "Phytochemical Assay & Analysis"]
      });
      window.showToast?.(`Government opportunity published nationwide!`, 'success');
      overlay.classList.remove('active');
      window.navigateToTab('programs');
    } catch (err) {
      window.showToast?.(err.message, 'danger');
    }
  };
}

export function openCreateHackathonModal() {
  const modalContainer = document.getElementById('modal-container');
  modalContainer.innerHTML = `
    <div class="modal-card">
      <div class="modal-header">
        <h3><i class="fa-solid fa-trophy" style="color:var(--warning); margin-right:6px;"></i> Announce National Hackathon (SIH Model)</h3>
        <button class="btn btn-sm btn-secondary btn-close-modal"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">Hackathon Title</label>
          <input type="text" id="hack-title-input" class="form-control" value="Smart India AYUSH Challenge 2026 (SIH26044)" />
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label class="form-label">Theme / Domain</label>
            <input type="text" id="hack-theme-input" class="form-control" value="AI-Powered AYUSH Medicine Quality & Supply Intelligence" />
          </div>
          <div class="form-group">
            <label class="form-label">Prize Pool</label>
            <input type="text" id="hack-prizes-input" class="form-control" value="₹1,50,000 + Recruiter Fast-Track" />
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary btn-close-modal">Cancel</button>
        <button class="btn btn-primary" id="btn-confirm-hackathon"><i class="fa-solid fa-bullhorn"></i> Announce Hackathon</button>
      </div>
    </div>
  `;
  const overlay = document.getElementById('modal-overlay');
  overlay.classList.add('active');
  overlay.querySelectorAll('.btn-close-modal').forEach(b => {
    b.onclick = () => overlay.classList.remove('active');
  });

  document.getElementById('btn-confirm-hackathon').onclick = async () => {
    const title = document.getElementById('hack-title-input').value.trim();
    const theme = document.getElementById('hack-theme-input').value.trim();
    const prizes = document.getElementById('hack-prizes-input').value.trim();

    try {
      await api.post('/api/admin/hackathons', {
        title: title,
        theme: theme,
        problem_statements: [
          "SIH26044: Real AI-Powered Skill Intelligence Platform",
          "Automated Recruiter Verification and Anti-Scam Shield"
        ],
        prizes: prizes,
        registration_deadline: "15 Nov 2026",
        start_date: "22 Nov 2026",
        end_date: "24 Nov 2026"
      });
      window.showToast?.(`National Hackathon announced!`, 'success');
      overlay.classList.remove('active');
      window.navigateToTab('programs');
    } catch (err) {
      window.showToast?.(err.message, 'danger');
    }
  };
}
