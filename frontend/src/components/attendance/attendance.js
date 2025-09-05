(() => {
  "use strict";

  const NS = "aams";
  const ns = (k) => `${NS}:${k}`;
  const slug = (s) => s.toLowerCase().trim().replace(/\s+/g, "-");

  const save = (key, value) => localStorage.setItem(key, JSON.stringify(value));
  const load = (key, fallback) => {
    const v = localStorage.getItem(key);
    try { return v ? JSON.parse(v) : fallback; } catch { return fallback; }
  };

  // Key helpers
  const kBranches = ns("branches");
  const kDivs = (b) => ns(`branch:${slug(b)}:divisions`);
  const kSubs = (b, d) => ns(`branch:${slug(b)}:division:${slug(d)}:subjects`);
  const kStud = (b, d, s) =>
    ns(`branch:${slug(b)}:division:${slug(d)}:subject:${slug(s)}:students`);
  const kAttendance = (b, d, s, date) =>
    ns(`attendance:branch:${slug(b)}:division:${slug(d)}:subject:${slug(s)}:date:${date}`);

  // DOM
  const branchSelect = document.querySelector("#branchSelect");
  const divisionSelect = document.querySelector("#divisionSelect");
  const subjectSelect = document.querySelector("#subjectSelect");
  const attendanceDate = document.querySelector("#attendanceDate");
  const filterForm = document.querySelector("#attendanceFilter");
  const tableBody = document.querySelector("#attendanceTable tbody");
  const saveBtn = document.querySelector("#saveAttendance");

  // Data
  function getBranches() { return load(kBranches, []); }
  function getDivisions(b) { return load(kDivs(b), []); }
  function getSubjects(b, d) { return load(kSubs(b, d), []); }
  function getStudents(b, d, s) { return load(kStud(b, d, s), []); }

  // Populate selects
  function populateBranches() {
    branchSelect.innerHTML = `<option value="">Select Branch</option>`;
    getBranches().forEach(b => {
      branchSelect.innerHTML += `<option value="${b}">${b}</option>`;
    });
  }
  function populateDivisions(branch) {
    divisionSelect.innerHTML = `<option value="">Select Division</option>`;
    if (!branch) return;
    getDivisions(branch).forEach(d => {
      divisionSelect.innerHTML += `<option value="${d}">${d}</option>`;
    });
  }
  function populateSubjects(branch, division) {
    subjectSelect.innerHTML = `<option value="">Select Subject</option>`;
    if (!branch || !division) return;
    getSubjects(branch, division).forEach(s => {
      subjectSelect.innerHTML += `<option value="${s}">${s}</option>`;
    });
  }

  // Render student table
  function renderStudents(branch, division, subject, date) {
    tableBody.innerHTML = "";
    if (!branch || !division || !subject || !date) return;

    const students = getStudents(branch, division, subject);
    if (students.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="3">No students found.</td></tr>`;
      return;
    }

    // Load existing attendance if any
    const existing = load(kAttendance(branch, division, subject, date), {});
    students.forEach(st => {
      const status = existing[st.rollNo] || "absent"; // default absent
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${st.rollNo}</td>
        <td>${st.name}</td>
        <td>
          <button class="status-btn ${status}" data-roll="${st.rollNo}">
            ${status === "present" ? "Present" : "Absent"}
          </button>
        </td>
      `;
      tableBody.appendChild(tr);
    });
  }

  // Toggle status
  tableBody.addEventListener("click", (e) => {
    const btn = e.target.closest(".status-btn");
    if (!btn) return;
    btn.classList.toggle("present");
    btn.classList.toggle("absent");
    btn.textContent = btn.classList.contains("present") ? "Present" : "Absent";
  });

  // Load students
  filterForm.addEventListener("submit", (e) => {
    e.preventDefault();
    renderStudents(branchSelect.value, divisionSelect.value, subjectSelect.value, attendanceDate.value);
  });

  // Save attendance
  saveBtn.addEventListener("click", () => {
    const b = branchSelect.value;
    const d = divisionSelect.value;
    const s = subjectSelect.value;
    const date = attendanceDate.value;
    if (!b || !d || !s || !date) {
      alert("Please select all fields.");
      return;
    }

    const result = {};
    tableBody.querySelectorAll(".status-btn").forEach(btn => {
      result[btn.dataset.roll] = btn.classList.contains("present") ? "present" : "absent";
    });

    save(kAttendance(b, d, s, date), result);
    alert("Attendance saved successfully ✅");
  });

  // Cascading dropdowns
  branchSelect.addEventListener("change", () => {
    populateDivisions(branchSelect.value);
    populateSubjects("", "");
  });
  divisionSelect.addEventListener("change", () => {
    populateSubjects(branchSelect.value, divisionSelect.value);
  });

  // Init
  document.addEventListener("DOMContentLoaded", () => {
    populateBranches();
  });
})();
