// Copied from src/components/teacher/teacher.js
requireTeacher?.();
const userIcon = document.getElementById("userIcon");
const userSidebar = document.getElementById("userSidebar");
userIcon.addEventListener("click", () => { userSidebar.classList.toggle("active"); });
window.addEventListener("click", (e) => { if (!userSidebar.contains(e.target) && !userIcon.contains(e.target)) { userSidebar.classList.remove("active"); } });
const sidebarAvatar = document.getElementById("sidebarAvatar");
const sidebarName = document.getElementById("sidebarName");
const sidebarRole = document.getElementById("sidebarRole");
const teacherName = document.getElementById("teacherName");
const teacherRole = document.getElementById("teacherRole");
const teacherEmail = document.getElementById("teacherEmail");
const teacherPassword = document.getElementById("teacherPassword");
const profileUpload = document.getElementById("profileUpload");
const saveInfoBtn = document.getElementById("saveInfoBtn");
const logoutBtn = document.getElementById("logoutBtn");
window.addEventListener("load", () => {
  if (localStorage.getItem("teacherName")) { teacherName.value = localStorage.getItem("teacherName"); sidebarName.textContent = localStorage.getItem("teacherName"); }
  if (localStorage.getItem("teacherRole")) { teacherRole.value = localStorage.getItem("teacherRole"); sidebarRole.textContent = localStorage.getItem("teacherRole"); }
  if (localStorage.getItem("teacherEmail")) teacherEmail.value = localStorage.getItem("teacherEmail");
  if (localStorage.getItem("teacherPassword")) teacherPassword.value = localStorage.getItem("teacherPassword");
  if (localStorage.getItem("teacherProfileImage")) { sidebarAvatar.src = localStorage.getItem("teacherProfileImage"); }
});
profileUpload.addEventListener("change", e => { const file = e.target.files[0]; if (file) { const reader = new FileReader(); reader.onload = () => { sidebarAvatar.src = reader.result; localStorage.setItem("teacherProfileImage", reader.result); }; reader.readAsDataURL(file); } });
saveInfoBtn.addEventListener("click", () => { localStorage.setItem("teacherName", teacherName.value); localStorage.setItem("teacherRole", teacherRole.value); localStorage.setItem("teacherEmail", teacherEmail.value); localStorage.setItem("teacherPassword", teacherPassword.value); sidebarName.textContent = teacherName.value; sidebarRole.textContent = teacherRole.value; alert("Teacher Info Saved!"); });
logoutBtn.addEventListener("click", () => { logout(); });
