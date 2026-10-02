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
        if (typeof login === "function") {
            const user = await login(email, password, role);
            
            // Redirect based on role returned from server (source of truth)
            if(user.role === "teacher") {
                window.location.href = "teacher.html";
            } else if(user.role === "admin") {
                window.location.href = "dashboard.html";
            } else {
                window.location.href = "student.html";
            }
        } else {
            console.error("Auth module missing.");
            alert("Error: Auth module not loaded.");
        }
    } catch(err) {
        console.error(err);
        // Alert is handled inside login()
    }
});
