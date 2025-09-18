document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");
    const logoutBtn = document.getElementById("logoutBtn");
    const welcomeMessage = document.getElementById("welcomeMessage");
    const roleMessage = document.getElementById("roleMessage");
    const reportCards = document.getElementById("reportCards");

    const user = getCurrentUser(); // From auth.js
    if(!user) {
        alert("Not logged in!");
        window.location.href = "login.html";
        return;
    }

    const role = user.role.toLowerCase();

    // Sidebar info
    document.getElementById("sidebarName").textContent = user.full_name || "User";
    document.getElementById("sidebarRole").textContent = role.charAt(0).toUpperCase() + role.slice(1);

    // Welcome message
    if(role === "teacher") {
        welcomeMessage.textContent = `Welcome, Teacher ${user.full_name || ""}`;
        roleMessage.textContent = "Overview of class performance.";
    } else if(role === "student") {
        welcomeMessage.textContent = `Hey ${user.full_name || ""}!`;
        roleMessage.textContent = "Check your performance and attendance summary.";
    }

    // Cards
    const cardsData = role === "teacher" ? [
        { icon: "bx bx-line-chart", title: "Class Performance", link: "#" },
        { icon: "bx bx-group", title: "Student Comparison", link: "#" },
        { icon: "bx bx-list-check", title: "Individual Reports", link: "#" },
        { icon: "bx bx-bell", title: "Alerts & Notifications", link: "#" }
    ] : [
        { icon: "bx bx-calendar-check", title: "Attendance", link: "#" },
        { icon: "bx bx-line-chart", title: "Grades", link: "#" },
        { icon: "bx bx-bell", title: "Notifications", link: "#" }
    ];

    cardsData.forEach(card => {
        const div = document.createElement("div");
        div.className = "card";
        div.innerHTML = `<i class='${card.icon}'></i><h3>${card.title}</h3>`;
        div.addEventListener("click", () => window.location.href = card.link);
        reportCards.appendChild(div);
    });

    // Logout button
    logoutBtn.addEventListener("click", () => {
        logoutUser();
        window.location.href = "login.html";
    });

    // Charts placeholders
    const attendanceCtx = document.getElementById("attendanceChart").getContext("2d");
    const gradesCtx = document.getElementById("gradesChart").getContext("2d");

    new Chart(attendanceCtx, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Attendance %', data: [], backgroundColor: 'rgba(99,99,255,0.2)', borderColor: 'rgba(99,99,255,1)', borderWidth: 2 }] },
        options: { responsive: true, maintainAspectRatio: false, layout: { padding: 10 } }
    });

    new Chart(gradesCtx, {
        type: 'bar',
        data: { labels: [], datasets: [{ label: 'Grades', data: [], backgroundColor: 'rgba(99,99,255,0.6)' }] },
        options: { responsive: true, maintainAspectRatio: false, layout: { padding: 10 } }
    });
});
