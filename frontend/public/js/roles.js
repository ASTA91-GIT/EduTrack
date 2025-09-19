// public/js/roles.js

function isTeacher() {
  const user = getCurrentUser();
  return !!user && String(user.role).toLowerCase() === "teacher";
}

function isStudent() {
  const user = getCurrentUser();
  return !!user && String(user.role).toLowerCase() === "student";
}

function requireTeacher() {
  protectPage("teacher");
}

function requireStudent() {
  protectPage("student");
}
