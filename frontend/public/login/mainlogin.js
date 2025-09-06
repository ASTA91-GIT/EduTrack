document.getElementById("loginForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value.trim();
  const role = document.getElementById("loginRole").value;

  const users = JSON.parse(localStorage.getItem("aamsUsers")) || [];
  const user = users.find(u => u.email === email && u.password === password && u.role === role);

  if (!user) { 
    alert("Invalid credentials or role. Please try again."); 
    return; 
  }

  localStorage.setItem("aamsCurrentUser", JSON.stringify(user));

  if (role === "teacher") {
    window.location.href = "teacher.html";   // ✅ relative path
  } else if (role === "student") {
    window.location.href = "student.html";   // ✅ relative path
  }
});
