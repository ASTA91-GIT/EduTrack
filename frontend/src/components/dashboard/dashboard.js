
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
    if(user.role === "teacher"){
        welcomeMessage.textContent = `Welcome Teacher ${user.full_name || ""}!`;
        roleMessage.textContent = `Manage your classes efficiently.`;
    } else {
        welcomeMessage.textContent = `Hey ${user.full_name || ""}!`;
        roleMessage.textContent = `Stay motivated! Your attendance is key to success.`;
    }

    // Sidebar info
    document.getElementById("sidebarName").textContent = user.full_name || "User";
    document.getElementById("sidebarRole").textContent = user.role;
    document.getElementById("teacherName").value = user.full_name || "";
    document.getElementById("teacherRole").value = user.role;
    document.getElementById("teacherEmail").value = user.email || "";

    // Logout
    logoutBtn.addEventListener("click", () => {
        localStorage.removeItem("aamsCurrentUser");
        window.location.href="login.html";
    });

    saveInfoBtn.addEventListener("click", () => alert("Personal info saved (mock)."));

    // Fetch dashboard cards from backend
    try {
        const res = await fetch(`http://127.0.0.1:8000/api/dashboard?role=${user.role}`);
        const data = await res.json();

        dashboardCards.innerHTML = "";
        data.cards.forEach(card => {
            const div = document.createElement("div");
            div.className="card";
            div.innerHTML=`<i class='${card.icon}'></i><h3>${card.title}</h3>`;
            div.addEventListener("click",()=>window.location.href=card.link);
            dashboardCards.appendChild(div);
        });

        // Fetch chart data
        const attendanceRes = await fetch(`http://127.0.0.1:8000/api/attendance?user_id=${user.id}`);
        const attendanceData = await attendanceRes.json();
        renderChart("attendanceChart", attendanceData.subjects, attendanceData.percentages, "Attendance %");

        const testsRes = await fetch(`http://127.0.0.1:8000/api/tests/upcoming?user_id=${user.id}`);
        const testsData = await testsRes.json();
        renderChart("testsChart", testsData.tests, testsData.scores, "Upcoming Tests");

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
