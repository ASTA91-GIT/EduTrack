/**
 * EduTrack Shared App Shell (Sidebar, Topbar, Theme Toggle, Profile, Font Awesome 6 Icons)
 */

(function () {
  // 1. Immediate theme initialization to prevent flash of wrong theme
  const savedTheme = localStorage.getItem('edutrack_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
})();

function renderAppShell(config = {}) {
  const activePage = config.activePage || 'dashboard';
  const pageTitle = config.pageTitle || 'Dashboard';
  const breadcrumb = config.breadcrumb || 'Dashboard';

  const user = (typeof getCurrentUser === 'function' && getCurrentUser()) || {
    full_name: 'Academic User',
    email: 'user@edutrack.local',
    role: 'student'
  };

  const isTeacher = user.role === 'teacher';
  const dashboardLink = isTeacher ? 'teacher.html' : 'student.html';

  const sidebarHtml = `
    <aside class="sidebar" id="appSidebar">
      <a href="${dashboardLink}" class="sidebar-brand">
        <div class="brand-icon-wrap">
          <i class="fa-solid fa-graduation-cap"></i>
        </div>
        <div class="brand-title">Edu<span>Track</span></div>
      </a>

      <div class="sidebar-nav">
        <div>
          <div class="nav-section-title">Overview</div>
          <a href="${dashboardLink}" class="nav-item ${activePage === 'dashboard' ? 'active' : ''}">
            <i class="fa-solid fa-table-columns"></i>
            <span>Dashboard</span>
          </a>
        </div>

        <div>
          <div class="nav-section-title">Academics</div>
          <a href="attendance.html" class="nav-item ${activePage === 'attendance' ? 'active' : ''}">
            <i class="fa-solid fa-clipboard-check"></i>
            <span>Attendance</span>
          </a>
          <a href="timetable.html" class="nav-item ${activePage === 'timetable' ? 'active' : ''}">
            <i class="fa-solid fa-calendar-days"></i>
            <span>Timetable</span>
          </a>
          <a href="lectures.html" class="nav-item ${activePage === 'lectures' ? 'active' : ''}">
            <i class="fa-solid fa-chalkboard-user"></i>
            <span>Lectures</span>
          </a>
          <a href="resources.html" class="nav-item ${activePage === 'resources' ? 'active' : ''}">
            <i class="fa-solid fa-folder-open"></i>
            <span>Resources</span>
          </a>
          <a href="events.html" class="nav-item ${activePage === 'events' ? 'active' : ''}">
            <i class="fa-solid fa-calendar-check"></i>
            <span>Events</span>
          </a>
        </div>

        <div>
          <div class="nav-section-title">Insights</div>
          <a href="analytics.html" class="nav-item ${activePage === 'analytics' ? 'active' : ''}">
            <i class="fa-solid fa-chart-line"></i>
            <span>Analytics</span>
          </a>
          <a href="reports.html" class="nav-item ${activePage === 'reports' ? 'active' : ''}">
            <i class="fa-solid fa-file-export"></i>
            <span>Reports</span>
          </a>
        </div>
      </div>

      <div class="sidebar-footer">
        <a href="profile.html" class="nav-item ${activePage === 'profile' ? 'active' : ''}" style="padding: 8px 12px;">
          <i class="fa-solid fa-circle-user"></i>
          <span>Profile</span>
        </a>
        <a href="settings.html" class="nav-item ${activePage === 'settings' ? 'active' : ''}" style="padding: 8px 12px;">
          <i class="fa-solid fa-gear"></i>
          <span>Settings</span>
        </a>
        <a href="javascript:void(0)" onclick="logout()" class="nav-item" style="padding: 8px 12px; color: var(--danger);">
          <i class="fa-solid fa-right-from-bracket"></i>
          <span>Logout</span>
        </a>

        <a href="profile.html" class="sidebar-user" style="margin-top: 6px;">
          <div class="user-avatar-circle">
            ${(user.full_name || 'U').charAt(0).toUpperCase()}
          </div>
          <div class="user-meta">
            <span class="user-name-txt">${escapeHtml(user.full_name || 'User')}</span>
            <span class="user-role-badge">${escapeHtml(user.role || 'student')}</span>
          </div>
        </a>
      </div>
    </aside>
  `;

  const topbarHtml = `
    <header class="topbar">
      <div class="topbar-left">
        <button class="mobile-menu-btn" id="mobileMenuBtn" aria-label="Toggle navigation">
          <i class="fa-solid fa-bars"></i>
        </button>
        <div class="breadcrumb-nav">
          <a href="${dashboardLink}">EduTrack</a>
          <span>/</span>
          <span class="breadcrumb-current">${escapeHtml(breadcrumb)}</span>
        </div>
      </div>

      <div class="topbar-right">
        <div class="search-input-wrap">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input type="text" placeholder="Search academics..." id="globalSearchInput" />
        </div>

        <button class="icon-action-btn" id="themeToggleBtn" title="Toggle Theme" aria-label="Toggle light/dark theme">
          <i class="fa-solid ${document.documentElement.getAttribute('data-theme') === 'light' ? 'fa-moon' : 'fa-sun'}"></i>
        </button>

        <a href="notifications.html" class="icon-action-btn" title="Notifications" aria-label="Notifications">
          <i class="fa-solid fa-bell"></i>
          <span class="badge-dot"></span>
        </a>

        <a href="profile.html" class="icon-action-btn" title="My Profile" aria-label="User profile">
          <i class="fa-solid fa-circle-user"></i>
        </a>
      </div>
    </header>
  `;

  return { sidebarHtml, topbarHtml };
}

function initAppShell(config = {}) {
  const { sidebarHtml, topbarHtml } = renderAppShell(config);

  const sidebarMount = document.getElementById('sidebar-mount');
  if (sidebarMount) {
    sidebarMount.innerHTML = sidebarHtml;
  }

  const topbarMount = document.getElementById('topbar-mount');
  if (topbarMount) {
    topbarMount.innerHTML = topbarHtml;
  }

  // Mobile menu toggle
  const mobileBtn = document.getElementById('mobileMenuBtn');
  const sidebar = document.getElementById('appSidebar');
  if (mobileBtn && sidebar) {
    mobileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      sidebar.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
      if (!sidebar.contains(e.target) && !mobileBtn.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // Theme toggle
  const themeBtn = document.getElementById('themeToggleBtn');
  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('edutrack_theme', next);

      // Re-render icon
      themeBtn.innerHTML = `<i class="fa-solid ${next === 'light' ? 'fa-moon' : 'fa-sun'}"></i>`;
    });
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

window.initAppShell = initAppShell;
