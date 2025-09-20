
document.addEventListener("DOMContentLoaded", async () => {
    const sidebar = document.getElementById("userSidebar");
    const profileIcon = document.getElementById("userIcon");
    const logoutBtn = document.getElementById("logoutBtn");
    const saveInfoBtn = document.getElementById("saveInfoBtn");
    const welcomeMessage = document.getElementById("welcomeMessage");
    const roleMessage = document.getElementById("roleMessage");
    const dashboardCards = document.getElementById("dashboardCards");

    profileIcon.addEventListener("click", () => sidebar.classList.toggle("active"));

    const user = JSON.parse(localStorage.getItem("aamsCurrentUser"));
    if(!user) { window.location.href="login.html"; return; }

    // Dynamic welcome & role message
    const safeName = (user.full_name || "").toString();
    if(user.role === "teacher"){
        welcomeMessage.textContent = `Welcome Teacher ${safeName}!`;
        roleMessage.textContent = `Manage your classes efficiently.`;
    } else {
        welcomeMessage.textContent = `Hey ${safeName}!`;
        roleMessage.textContent = `Stay motivated! Your attendance is key to success.`;
    }

    // Sidebar info
    document.getElementById("sidebarName").textContent = safeName || "User";
    document.getElementById("sidebarRole").textContent = user.role;
    document.getElementById("teacherName").value = safeName || "";
    document.getElementById("teacherRole").value = user.role;
    document.getElementById("teacherEmail").value = (user.email || "").toString();

    // Logout
    logoutBtn.addEventListener("click", () => {
        try { logout(); } catch { window.location.href="login.html"; }
    });

    saveInfoBtn.addEventListener("click", () => alert("Personal info saved (mock)."));

    // Fetch dashboard cards from backend (authenticated)
    try {
        const cardsRes = await authFetch(`http://127.0.0.1:8000/api/dashboard?role=${encodeURIComponent(user.role)}`);
        if (!cardsRes.ok) throw new Error("Failed to load dashboard cards");
        const data = await cardsRes.json();

        dashboardCards.innerHTML = "";
        (data.cards || []).forEach(card => {
            const div = document.createElement("div");
            div.className = "card";
            const icon = (card.icon || "").toString();
            const title = (card.title || "").toString();
            div.innerHTML = `<i class='${icon.replace(/'/g, "&apos;")}'></i><h3></h3>`;
            const h3 = div.querySelector("h3");
            h3.textContent = title;
            const link = (card.link || "").toString();
            div.addEventListener("click",()=>{ if (link) window.location.href = link; });
            dashboardCards.appendChild(div);
        });

        // Fetch chart data (authenticated)
        const attendanceRes = await authFetch(`http://127.0.0.1:8000/api/attendance?user_id=${encodeURIComponent(user.id)}`);
        if (attendanceRes.ok) {
            const attendanceData = await attendanceRes.json();
            renderChart("attendanceChart", attendanceData.subjects || [], attendanceData.percentages || [], "Attendance %");
        }

        const testsRes = await authFetch(`http://127.0.0.1:8000/api/tests/upcoming?user_id=${encodeURIComponent(user.id)}`);
        if (testsRes.ok) {
            const testsData = await testsRes.json();
            renderChart("testsChart", testsData.tests || [], testsData.scores || [], "Upcoming Tests");
        }

    } catch(err){
        console.error("Dashboard fetch error:", err);
    }
});

function renderChart(canvasId, labels, data, label){
    const ctx = document.getElementById(canvasId).getContext("2d");
    new Chart(ctx,{
        type:"bar",
        data:{ labels, datasets:[{ label, data, backgroundColor:"rgba(75,108,183,0.7)" }] },
        options:{ responsive:true, plugins:{ legend:{ display:false } }, scales:{ y:{ beginAtZero:true, max:100 } } }
    });
}
