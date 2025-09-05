(() => {
  "use strict";

  const NS = "aams";
  const ns = (k) => `${NS}:${k}`;
  const slug = (s) => s.toLowerCase().trim().replace(/\s+/g, "-");
  const load = (key, fb) => {
    const v = localStorage.getItem(key);
    try { return v ? JSON.parse(v) : fb; } catch { return fb; }
  };

  // Keys
  const kBranches = ns("branches");
  const kDivs = (b) => ns(`branch:${slug(b)}:divisions`);
  const kSubs = (b, d) => ns(`branch:${slug(b)}:division:${slug(d)}:subjects`);
  const kStud = (b, d, s) => ns(`branch:${slug(b)}:division:${slug(d)}:subject:${slug(s)}:students`);
  const kAttendance = (b, d, s, date) =>
    ns(`attendance:branch:${slug(b)}:division:${slug(d)}:subject:${slug(s)}:date:${date}`);

  // DOM
  const branchSel = document.querySelector("#branchSelect");
  const divSel = document.querySelector("#divisionSelect");
  const subSel = document.querySelector("#subjectSelect");
  const fromDate = document.querySelector("#fromDate");
  const toDate = document.querySelector("#toDate");
  const reportForm = document.querySelector("#reportFilter");
  const tbody = document.querySelector("#reportTable tbody");

  // Populate dropdowns
  function populateBranches() {
    branchSel.innerHTML = `<option value="">Select Branch</option>`;
    load(kBranches, []).forEach(b => {
      branchSel.innerHTML += `<option value="${b}">${b}</option>`;
    });
  }
  function populateDivisions(branch) {
    divSel.innerHTML = `<option value="">Select Division</option>`;
    if (!branch) return;
    load(kDivs(branch), []).forEach(d => {
      divSel.innerHTML += `<option value="${d}">${d}</option>`;
    });
  }
  function populateSubjects(branch, division) {
    subSel.innerHTML = `<option value="">Select Subject</option>`;
    if (!branch || !division) return;
    load(kSubs(branch, division), []).forEach(s => {
      subSel.innerHTML += `<option value="${s}">${s}</option>`;
    });
  }

  // Generate report
  function generateReport(b, d, s, from, to) {
    tbody.innerHTML = "";
    const students = load(kStud(b, d, s), []);
    if (students.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6">No students found.</td></tr>`;
      return;
    }

    const fromDt = new Date(from);
    const toDt = new Date(to);
    const stats = {};
    students.forEach(st => stats[st.rollNo] = { name: st.name, total: 0, present: 0 });

    for (let dt = new Date(fromDt); dt <= toDt; dt.setDate(dt.getDate() + 1)) {
      const dateStr = dt.toISOString().split("T")[0];
      const att = load(kAttendance(b, d, s, dateStr), null);
      if (!att) continue;
      Object.keys(stats).forEach(roll => {
        stats[roll].total++;
        if (att[roll] === "present") stats[roll].present++;
      });
    }

    // Fill table
    Object.entries(stats).forEach(([roll, st]) => {
      const absent = st.total - st.present;
      const perc = st.total > 0 ? Math.round((st.present / st.total) * 100) : 0;
      tbody.innerHTML += `
        <tr>
          <td>${roll}</td>
          <td>${st.name}</td>
          <td>${st.total}</td>
          <td>${st.present}</td>
          <td>${absent}</td>
          <td>${perc}%</td>
        </tr>
      `;
    });

    renderCharts(stats);
  }

  // Charts
  let overallChart, studentChart;
  function renderCharts(stats) {
    const ctxOverall = document.querySelector("#chartOverall").getContext("2d");
    const ctxStudent = document.querySelector("#chartPerStudent").getContext("2d");

    const total = Object.values(stats).reduce((a, s) => a + s.total, 0);
    const present = Object.values(stats).reduce((a, s) => a + s.present, 0);
    const absent = total - present;

    if (overallChart) overallChart.destroy();
    overallChart = new Chart(ctxOverall, {
      type: "doughnut",
      data: {
        labels: ["Present", "Absent"],
        datasets: [{ data: [present, absent], backgroundColor: ["#10b981", "#ef4444"] }]
      }
    });

    if (studentChart) studentChart.destroy();
    studentChart = new Chart(ctxStudent, {
      type: "bar",
      data: {
        labels: Object.keys(stats),
        datasets: [{
          label: "% Attendance",
          data: Object.values(stats).map(s => s.total ? Math.round((s.present / s.total) * 100) : 0),
          backgroundColor: "#6366f1"
        }]
      },
      options: { scales: { y: { beginAtZero: true, max: 100 } } }
    });
  }

  // Events
  branchSel.addEventListener("change", () => {
    populateDivisions(branchSel.value);
    populateSubjects("", "");
  });
  divSel.addEventListener("change", () => {
    populateSubjects(branchSel.value, divSel.value);
  });
  reportForm.addEventListener("submit", e => {
    e.preventDefault();
    generateReport(branchSel.value, divSel.value, subSel.value, fromDate.value, toDate.value);
  });

  // Init
  document.addEventListener("DOMContentLoaded", () => {
    populateBranches();
  });
})();
