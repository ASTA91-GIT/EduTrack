const registerForm = document.getElementById("registerForm");

if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const role = "student";
    const name = document.getElementById("regName").value;
    const email = document.getElementById("regEmail").value;
    const password = document.getElementById("regPassword").value;

    try {
      const user = await register(name, email, password, role);

      // Redirect based on role
      if (user.role === "admin") {
        window.location.href = "dashboard.html";
      } else if (user.role === "teacher") {
        window.location.href = "teacher.html";
      } else {
        window.location.href = "student.html";
      }
    } catch (err) {
      // Error handled in auth.js alert
      console.error(err);
    }
  });
}
