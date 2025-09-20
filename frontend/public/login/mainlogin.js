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
        // Use shared login() from public/js/auth.js if available
        if (typeof login === "function") {
            const user = await login(email, password);
            // overwrite role with selected one if backend didn't return
            if (!user.role) user.role = role;
            localStorage.setItem("aamsCurrentUser", JSON.stringify(user));
        } else {
            const res = await fetch("http://127.0.0.1:8000/api/auth/login", {
                method: "POST",
                headers: {"Content-Type":"application/json"},
                body: JSON.stringify({email, password, role})
            });

            if(!res.ok){
                const data = await res.json().catch(() => ({}));
                alert(data.detail || "Login failed!");
                return;
            }
            const user = await res.json();
            localStorage.setItem("aamsCurrentUser", JSON.stringify(user));
        }

        const finalUser = JSON.parse(localStorage.getItem("aamsCurrentUser"));
        if(finalUser?.role === "teacher") {
            window.location.href = "teacher.html";
        } else {
            window.location.href = "dashboard.html";
        }

    } catch(err) {
        console.error(err);
        alert("Error connecting to server.");
    }
});
