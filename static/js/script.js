// ── Auto-dismiss flash messages ───────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  const alerts = document.querySelectorAll('.auto-dismiss');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 4000);
  });

  // ── Password visibility toggle ─────────────────────────────────────────────
  document.querySelectorAll('.password-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const input = this.previousElementSibling;
      const icon = this.querySelector('i');
      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
      } else {
        input.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
      }
    });
  });

  // ── Delete confirmation ────────────────────────────────────────────────────
  document.querySelectorAll('.confirm-delete').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
        e.preventDefault();
      }
    });
  });

  // ── Return confirmation ────────────────────────────────────────────────────
  document.querySelectorAll('.confirm-return').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!confirm('Confirm return of this book? Any applicable fine will be calculated.')) {
        e.preventDefault();
      }
    });
  });

  // ── Admin sidebar mobile toggle ────────────────────────────────────────────
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('adminSidebar');
  const overlay = document.getElementById('sidebarOverlay');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('show');
      if (overlay) overlay.classList.toggle('show');
    });
    if (overlay) {
      overlay.addEventListener('click', function () {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
      });
    }
  }

  // ── Search debounce ────────────────────────────────────────────────────────
  const searchInput = document.getElementById('liveSearch');
  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        searchInput.closest('form').submit();
      }, 500);
    });
  }

  // ── Highlight overdue rows ─────────────────────────────────────────────────
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  document.querySelectorAll('[data-due-date]').forEach(function (el) {
    const due = new Date(el.dataset.dueDate);
    due.setHours(0, 0, 0, 0);
    if (due < today) {
      const row = el.closest('tr');
      if (row) row.classList.add('overdue-row');
    }
  });
});

// ── Chart.js color palette ─────────────────────────────────────────────────────
const COLORS = [
  '#1a2744', '#c9a84c', '#3b5999', '#e8c96a', '#243360',
  '#6b7280', '#d97706', '#10b981', '#ef4444', '#8b5cf6'
];

function renderCategoryChart(canvasId, labels, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{ data: data, backgroundColor: COLORS, borderWidth: 2, borderColor: '#fff' }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { boxWidth: 14, font: { size: 12 } } }
      }
    }
  });
}

function renderLineChart(canvasId, labels, datasets) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: datasets.map((d, i) => ({
        label: d.label,
        data: d.data,
        borderColor: COLORS[i],
        backgroundColor: COLORS[i] + '22',
        tension: 0.4,
        fill: true,
        pointRadius: 4,
        pointHoverRadius: 7,
        borderWidth: 2
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'top' } },
      scales: {
        y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: '#f3f4f6' } },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderBarChart(canvasId, labels, data, label) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: label || 'Count',
        data: data,
        backgroundColor: COLORS,
        borderRadius: 6,
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: '#f3f4f6' } },
        x: { grid: { display: false }, ticks: { maxRotation: 45 } }
      }
    }
  });
}
