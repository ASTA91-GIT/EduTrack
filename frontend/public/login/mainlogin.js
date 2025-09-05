const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () => {
  container.classList.add("active");
});

loginBtn.addEventListener('click', () => {
  container.classList.remove("active");
});

let users = JSON.parse(localStorage.getItem("aamsUsers")) || [];

document.getElementById("registerForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const name = this.querySelector('input[placeholder="Full Name"]').value.trim();
  const email = this.querySelector('input[placeholder="Institutional Email"]').value.trim();
  const password = this.querySelector('input[placeholder="Password"]').value.trim();
  const role = document.getElementById("registerRole").value;
  if (!name || !email || !password || !role) { alert("Please fill all fields."); return; }
  const existing = users.find(u => u.email === email && u.role === role);
  if (existing) { alert("Account already exists for this email and role!"); return; }
  users.push({ name, email, password, role });
  localStorage.setItem("aamsUsers", JSON.stringify(users));
  alert("Registration successful! Please login.");
  container.classList.remove("active");
});

document.getElementById("loginForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value.trim();
  const role = document.getElementById("loginRole").value;
  const user = users.find(u => u.email === email && u.password === password && u.role === role);
  if (!user) { alert("Invalid credentials or role. Please try again."); return; }
  localStorage.setItem("aamsCurrentUser", JSON.stringify(user));
  if (role === "teacher") {
    window.location.href = "/teacher.html";
  } else if (role === "student") {
    window.location.href = "/student.html";
  }
});

