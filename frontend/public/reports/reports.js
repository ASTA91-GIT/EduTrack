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

    const role = String(user.role || "").toLowerCase();

    // Sidebar info
    document.getElementById("sidebarName").textContent = (user.full_name || "User").toString();
    document.getElementById("sidebarRole").textContent = role.charAt(0).toUpperCase() + role.slice(1);

    // Welcome message
    if(role === "teacher") {
        welcomeMessage.textContent = `Welcome, Teacher ${(user.full_name || "").toString()}`;
        roleMessage.textContent = "Overview of class performance.";
    } else if(role === "student") {
        welcomeMessage.textContent = `Hey ${(user.full_name || "").toString()}!`;
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
        const icon = (card.icon || "").toString().replace(/'/g, "&apos;");
        const title = (card.title || "").toString();
        div.innerHTML = `<i class='${icon}'></i><h3></h3>`;
        div.querySelector("h3").textContent = title;
        const href = (card.link || "").toString();
        div.addEventListener("click", () => { if (href) window.location.href = href; });
        reportCards.appendChild(div);
    });

    // Logout button
    logoutBtn.addEventListener("click", () => {
        logout();
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
