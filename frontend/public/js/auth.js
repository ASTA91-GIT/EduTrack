// public/js/auth.js

// Get current logged-in user
const currentUser = JSON.parse(localStorage.getItem("aamsCurrentUser"));

// Function to protect a page
function protectPage(requiredRole) {
  if (!currentUser) {
    // Not logged in
    window.location.href = "login.html";
    return;
  }

  if (requiredRole && currentUser.role !== requiredRole) {
    // Logged in but wrong role
    window.location.href = "login.html";
  }
}

// Function to logout
function logout() {
  localStorage.removeItem("aamsCurrentUser");
  window.location.href = "login.html";
}

