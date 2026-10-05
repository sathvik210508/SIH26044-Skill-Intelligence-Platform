/**
 * SIH26044 — Master Frontend Application Controller
 * Role-Based Portal Architecture & State Management
 */

import { api } from './api.js';
import { auth } from './auth.js';
import {
  renderStudentDashboard,
  renderStudentProfile,
  renderStudentSkills,
  renderStudentSkillGaps,
  renderStudentCareerMatches,
  renderStudentJobs
} from './student_portal.js';

import {
  renderRecruiterDashboard,
  renderRecruiterJobs,
  renderRecruiterCandidates,
  renderRecruiterAnalytics
} from './recruiter_portal.js';

import {
  renderInstitutionDashboard,
  renderStudentRosterView,
  renderInstitutionHeatmapView,
  renderPlacementIntelligenceView,
  renderWorkshopsView
} from './institution_portal.js';

import {
  renderAdminDashboard,
  renderInstitutionsPRSView,
  renderCompanyVerificationView,
  renderSupplyDemandView,
  renderHackathonsAndSchemesView
} from './admin_portal.js';

import { aiAssistant } from './ai_assistant.js';

let currentActiveTab = 'dashboard';
let authenticatedAppInitialized = false;

// Global Toast Notification
window.showToast = function(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  const icon = type === 'success' ? 'fa-circle-check' : (type === 'danger' ? 'fa-circle-exclamation' : (type === 'warning' ? 'fa-triangle-exclamation' : 'fa-circle-info'));
  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.25s ease';
    setTimeout(() => toast.remove(), 250);
  }, 3500);
};

// Global Navigation Dispatcher
window.navigateToTab = function(tabName) {
  currentActiveTab = tabName;
  updateSidebarActiveItem();
  renderActiveView();
};

async function initApp() {
  // A dashboard is only available after login or registration.
  if (!auth.isAuthenticated()) {
    showAuthScreen();
    setupAuthForms();
    return;
  }

  // Do not expose a dashboard for an expired or otherwise invalid saved token.
  try {
    await api.get('/api/auth/me');
  } catch (err) {
    auth.logout();
    showAuthScreen();
    setupAuthForms();
    return;
  }

  showApplication();
  startAuthenticatedApp();
}

function startAuthenticatedApp() {
  if (authenticatedAppInitialized) return;
  authenticatedAppInitialized = true;

  // Listen to auth changes
  auth.onAuthChange((user) => {
    updateUserInterface(user);
    renderActiveView();
    fetchNotifications();
  });

  setupLogout();

  // Setup Notifications
  setupNotifications();

  // Init AI Assistant
  aiAssistant.init();

  // Initial render
  const user = auth.getUser();
  updateUserInterface(user);
  renderActiveView();
  fetchNotifications();

  // Periodic notification fetch
  setInterval(fetchNotifications, 20000);
}

function showAuthScreen() {
  document.body.classList.remove('authenticated');
  document.getElementById('auth-screen').hidden = false;
}

function showApplication() {
  document.body.classList.add('authenticated');
  document.getElementById('auth-screen').hidden = true;
}

function setupAuthForms() {
  document.querySelectorAll('.auth-tab').forEach(tab => {
    tab.onclick = () => setAuthMode(tab.dataset.authMode);
  });

  document.getElementById('login-form').onsubmit = async (event) => {
    event.preventDefault();
    const error = document.getElementById('login-error');
    error.textContent = '';
    try {
      const user = await auth.login(
        document.getElementById('login-email').value.trim(),
        document.getElementById('login-password').value
      );
      finishAuthentication(user);
    } catch (err) {
      error.textContent = err.message || 'Unable to sign in. Please try again.';
    }
  };

  document.getElementById('signup-form').onsubmit = async (event) => {
    event.preventDefault();
    const error = document.getElementById('signup-error');
    const password = document.getElementById('signup-password').value;
    error.textContent = '';
    if (password !== document.getElementById('signup-confirm-password').value) {
      error.textContent = 'Passwords do not match.';
      return;
    }
    try {
      const user = await auth.register(
        document.getElementById('signup-email').value.trim(),
        password,
        document.getElementById('signup-name').value.trim(),
        document.getElementById('signup-role').value
      );
      finishAuthentication(user);
    } catch (err) {
      error.textContent = err.message || 'Unable to create your account. Please try again.';
    }
  };
}

function setAuthMode(mode) {
  const isLogin = mode === 'login';
  document.querySelectorAll('.auth-tab').forEach(tab => tab.classList.toggle('active', tab.dataset.authMode === mode));
  document.getElementById('login-form').hidden = !isLogin;
  document.getElementById('signup-form').hidden = isLogin;
  document.getElementById('auth-title').textContent = isLogin ? 'Welcome back' : 'Create your account';
  document.getElementById('auth-subtitle').textContent = isLogin ? 'Sign in to open your dashboard.' : 'Choose your role to get started.';
}

function finishAuthentication(user) {
  currentActiveTab = 'dashboard';
  showApplication();
  startAuthenticatedApp();
  updateUserInterface(user);
  renderActiveView();
  fetchNotifications();
  window.showToast(`Welcome, ${user.full_name}!`, 'success');
}

function setupLogout() {
  const logoutButton = document.getElementById('btn-logout');
  if (!logoutButton) return;
  logoutButton.onclick = () => {
    auth.logout();
    showAuthScreen();
    setAuthMode('login');
    document.getElementById('login-form').reset();
  };
}

function updateUserInterface(user) {
  if (!user) return;

  const currentUserName = document.getElementById('current-user-name');
  if (currentUserName) currentUserName.textContent = user.full_name;

  // Update Portal Badge
  const portalBadge = document.getElementById('sidebar-portal-badge');
  if (portalBadge) {
    portalBadge.className = `portal-badge ${user.role.toLowerCase()}`;
    portalBadge.innerText = `${user.role} PORTAL`;
  }

  // Re-render sidebar navigation for current role
  renderSidebarNav(user.role);
}

function renderSidebarNav(role) {
  const navContainer = document.getElementById('sidebar-nav-menu');
  if (!navContainer) return;

  let items = [];

  if (role === 'STUDENT') {
    items = [
      { id: 'dashboard', label: 'Dashboard', icon: 'fa-house' },
      { id: 'profile', label: 'My Profile', icon: 'fa-id-card' },
      { id: 'skills', label: 'My Skills', icon: 'fa-certificate' },
      { id: 'skill_gaps', label: 'Skill Gap Analysis', icon: 'fa-chart-pie' },
      { id: 'career_matches', label: 'Career Matches', icon: 'fa-compass' },
      { id: 'jobs', label: 'Jobs & Internships', icon: 'fa-briefcase' }
    ];
  } else if (role === 'RECRUITER') {
    items = [
      { id: 'dashboard', label: 'Dashboard', icon: 'fa-house' },
      { id: 'jobs', label: 'Job Postings', icon: 'fa-briefcase' },
      { id: 'candidates', label: 'Candidates', icon: 'fa-users-viewfinder' },
      { id: 'analytics', label: 'Hiring Analytics', icon: 'fa-chart-line' }
    ];
  } else if (role === 'INSTITUTION') {
    items = [
      { id: 'dashboard', label: 'Dashboard', icon: 'fa-house' },
      { id: 'students', label: 'Student Roster', icon: 'fa-users' },
      { id: 'heatmap', label: 'Skill Gap Heatmap', icon: 'fa-fire' },
      { id: 'placement', label: 'Placement Readiness', icon: 'fa-graduation-cap' },
      { id: 'workshops', label: 'Upskilling Programs', icon: 'fa-chalkboard-user' }
    ];
  } else if (role === 'ADMIN') {
    items = [
      { id: 'dashboard', label: 'National Dashboard', icon: 'fa-house' },
      { id: 'institutions', label: 'Institution PRS', icon: 'fa-landmark' },
      { id: 'companies', label: 'Company Verification', icon: 'fa-shield-check' },
      { id: 'supply_demand', label: 'Supply vs Demand', icon: 'fa-scale-balanced' },
      { id: 'programs', label: 'Hackathons & Schemes', icon: 'fa-trophy' }
    ];
  }

  // Ensure currentActiveTab is valid for this role
  if (!items.some(item => item.id === currentActiveTab)) {
    currentActiveTab = 'dashboard';
  }

  navContainer.innerHTML = items.map(item => `
    <li class="nav-item">
      <a class="nav-link ${currentActiveTab === item.id ? 'active' : ''}" data-tab="${item.id}">
        <i class="fa-solid ${item.icon}"></i>
        <span>${item.label}</span>
      </a>
    </li>
  `).join('');

  navContainer.querySelectorAll('.nav-link').forEach(link => {
    link.onclick = () => {
      currentActiveTab = link.dataset.tab;
      updateSidebarActiveItem();
      renderActiveView();
    };
  });
}

function updateSidebarActiveItem() {
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.dataset.tab === currentActiveTab) link.classList.add('active');
    else link.classList.remove('active');
  });
}

function renderActiveView() {
  const container = document.getElementById('viewport-container');
  if (!container) return;

  const role = auth.getRole() || 'STUDENT';
  const pageTitle = document.getElementById('page-main-title');
  const pageSubtitle = document.getElementById('page-sub-title');

  if (role === 'STUDENT') {
    if (currentActiveTab === 'dashboard') {
      if (pageTitle) pageTitle.innerText = "Student Dashboard";
      if (pageSubtitle) pageSubtitle.innerText = "Track your skills, discover suitable roles, and improve your career readiness.";
      renderStudentDashboard(container);
    } else if (currentActiveTab === 'profile') {
      if (pageTitle) pageTitle.innerText = "My Academic & Career Profile";
      if (pageSubtitle) pageSubtitle.innerText = "Verified student profile at National Institute of Ayurveda (NIA Jaipur).";
      renderStudentProfile(container);
    } else if (currentActiveTab === 'skills') {
      if (pageTitle) pageTitle.innerText = "My Verified Skills";
      if (pageSubtitle) pageSubtitle.innerText = "Calculated proficiency ratings, evidence verification, and adaptive test scores.";
      renderStudentSkills(container);
    } else if (currentActiveTab === 'skill_gaps') {
      if (pageTitle) pageTitle.innerText = "Skill Gap Analysis";
      if (pageSubtitle) pageSubtitle.innerText = "Target industry role benchmarks with curated learning roadmaps.";
      renderStudentSkillGaps(container);
    } else if (currentActiveTab === 'career_matches') {
      if (pageTitle) pageTitle.innerText = "AI Career & Role Matches";
      if (pageSubtitle) pageSubtitle.innerText = "Roles scored based on your verified skill metrics and industry demand.";
      renderStudentCareerMatches(container);
    } else if (currentActiveTab === 'jobs') {
      if (pageTitle) pageTitle.innerText = "Jobs & AYUSH Pharmaceutical Internships";
      if (pageSubtitle) pageSubtitle.innerText = "Opportunities matched against your verified skills matrix.";
      renderStudentJobs(container);
    }
  } else if (role === 'RECRUITER') {
    if (currentActiveTab === 'dashboard') {
      if (pageTitle) pageTitle.innerText = "Recruiter Talent Dashboard";
      if (pageSubtitle) pageSubtitle.innerText = "Candidate matching pipeline, verified skills evaluation, and active job postings.";
      renderRecruiterDashboard(container);
    } else if (currentActiveTab === 'jobs') {
      if (pageTitle) pageTitle.innerText = "Job Postings & Skill Matrix";
      if (pageSubtitle) pageSubtitle.innerText = "Define required competencies, thresholds, and importance weights.";
      renderRecruiterJobs(container);
    } else if (currentActiveTab === 'candidates') {
      if (pageTitle) pageTitle.innerText = "AI-Ranked Candidates";
      if (pageSubtitle) pageSubtitle.innerText = "Discover, compare, and interview candidates ranked by AI matching matrix.";
      renderRecruiterCandidates(container);
    } else if (currentActiveTab === 'analytics') {
      if (pageTitle) pageTitle.innerText = "Recruitment Funnel & Compliance";
      if (pageSubtitle) pageSubtitle.innerText = "Hiring yield, verification trust score, and university partnerships.";
      renderRecruiterAnalytics(container);
    }
  } else if (role === 'INSTITUTION') {
    if (currentActiveTab === 'dashboard') {
      if (pageTitle) pageTitle.innerText = "Institution Dashboard — NIA";
      if (pageSubtitle) pageSubtitle.innerText = "National Institute of Ayurveda (NIA Jaipur) pharmaceutical telemetry and readiness.";
      renderInstitutionDashboard(container);
    } else if (currentActiveTab === 'students') {
      if (pageTitle) pageTitle.innerText = "Student Roster & Skill Analytics";
      if (pageSubtitle) pageSubtitle.innerText = "Manage student records, filter by competency, and generate batch profiles.";
      renderStudentRosterView(container);
    } else if (currentActiveTab === 'heatmap') {
      if (pageTitle) pageTitle.innerText = "Institutional Skill Gap Heatmap";
      if (pageSubtitle) pageSubtitle.innerText = "Multi-year batch analysis identifying curriculum deficits and intervention needs.";
      renderInstitutionHeatmapView(container);
    } else if (currentActiveTab === 'placement') {
      if (pageTitle) pageTitle.innerText = "Placement Readiness & Corporate Hiring";
      if (pageSubtitle) pageSubtitle.innerText = "Placement statistics, hiring partner packages, and department performance.";
      renderPlacementIntelligenceView(container);
    } else if (currentActiveTab === 'workshops') {
      if (pageTitle) pageTitle.innerText = "Targeted Upskilling Workshops";
      if (pageSubtitle) pageSubtitle.innerText = "Organize targeted training programs and track measured pre vs post improvement.";
      renderWorkshopsView(container);
    }
  } else if (role === 'ADMIN') {
    if (currentActiveTab === 'dashboard') {
      if (pageTitle) pageTitle.innerText = "National Skill Intelligence Dashboard";
      if (pageSubtitle) pageSubtitle.innerText = "National Supply vs Demand, Platform Readiness Scores, and policy recommendations.";
      renderAdminDashboard(container);
    } else if (currentActiveTab === 'institutions') {
      if (pageTitle) pageTitle.innerText = "Institution PRS Leaderboard";
      if (pageSubtitle) pageSubtitle.innerText = "Accredited institution Platform Readiness Scores calculated via multi-signal formula.";
      renderInstitutionsPRSView(container);
    } else if (currentActiveTab === 'companies') {
      if (pageTitle) pageTitle.innerText = "Company & Employer Verification";
      if (pageSubtitle) pageSubtitle.innerText = "CIN verification, corporate authentication, and anti-scam registry management.";
      renderCompanyVerificationView(container);
    } else if (currentActiveTab === 'supply_demand') {
      if (pageTitle) pageTitle.innerText = "National Supply vs Demand Analysis";
      if (pageSubtitle) pageSubtitle.innerText = "Talent supply vs industry demand deficits and policy recommendations.";
      renderSupplyDemandView(container);
    } else if (currentActiveTab === 'programs') {
      if (pageTitle) pageTitle.innerText = "National AYUSH Challenges & Schemes";
      if (pageSubtitle) pageSubtitle.innerText = "Broadcast nationwide challenges (SIH model) and subsidized apprenticeships.";
      renderHackathonsAndSchemesView(container);
    }
  }
}

async function fetchNotifications() {
  if (!auth.isAuthenticated()) return;
  try {
    const notifs = await api.get('/api/notifications');
    const unread = notifs.filter(n => !n.is_read);
    const badge = document.getElementById('notif-badge-count');
    if (badge) {
      if (unread.length > 0) {
        badge.style.display = 'flex';
        badge.innerText = unread.length;
      } else {
        badge.style.display = 'none';
      }
    }
    renderNotificationsDropdown(notifs);
  } catch (err) {
    console.warn('Notification fetch warning:', err);
  }
}

function setupNotifications() {
  const bellBtn = document.getElementById('btn-notifications-bell');
  const dropdown = document.getElementById('notifications-dropdown');

  if (bellBtn && dropdown) {
    bellBtn.onclick = (e) => {
      e.stopPropagation();
      dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
    };

    document.addEventListener('click', (e) => {
      if (!dropdown.contains(e.target) && e.target !== bellBtn) {
        dropdown.style.display = 'none';
      }
    });
  }
}

function renderNotificationsDropdown(notifs) {
  const container = document.getElementById('notifications-list-container');
  if (!container) return;

  if (notifs.length === 0) {
    container.innerHTML = `<div style="padding:16px; text-align:center; color:var(--text-muted); font-size:0.82rem;">No new notifications.</div>`;
    return;
  }

  container.innerHTML = notifs.slice(0, 6).map(n => `
    <div style="padding:10px 14px; border-bottom:1px solid var(--border-light); background:${n.is_read ? '#FFFFFF' : 'var(--primary-light)'};">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <strong style="font-size:0.8rem; color:var(--text-primary);">${n.title}</strong>
        <span style="font-size:0.68rem; color:var(--text-muted);">${n.created_at || 'Just now'}</span>
      </div>
      <p style="font-size:0.75rem; color:var(--text-secondary); margin-top:2px;">${n.message}</p>
    </div>
  `).join('');
}

document.addEventListener('DOMContentLoaded', initApp);
