document.getElementById("loginForm").addEventListener("submit", async function(e){
    e.preventDefault();

    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim();
    const role = document.querySelector('input[name="role"]:checked')?.value;

    if(!email || !password || !role) {
        alert("Please fill all fields and select your role.");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:8000/api/auth/login", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({email, password, role})
        });

        if(!res.ok){
            const data = await res.json();
            alert(data.detail || "Login failed!");
            return;
        }

        const user = await res.json();
        localStorage.setItem("aamsCurrentUser", JSON.stringify(user));

        // Redirect based on role
        if(role === "teacher") {
            window.location.href = "teacher.html";
        } else if(role === "student") {
            window.location.href = "dashboard.html"; // Student sees dashboard
        }

    } catch(err) {
        console.error(err);
        alert("Error connecting to server.");
    }
});
