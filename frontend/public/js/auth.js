// public/js/auth.js

const API_URL = "http://localhost:8000/api"; // Adjust if deployed

// Get current logged-in user
const currentUser = JSON.parse(localStorage.getItem("aamsCurrentUser"));
const token = localStorage.getItem("edutrack_token");

// Function to login (call backend)
async function login(email, password) {
  try {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Login failed");
    }

    const data = await res.json();

    // Save token separately
    localStorage.setItem("edutrack_token", data.access_token);

    // Optional: decode JWT or fetch user info
    // For now, we store a minimal user object
    const user = {
      email,
      role: data.role || "student", // replace with actual field if backend sends role
    };

    localStorage.setItem("aamsCurrentUser", JSON.stringify(user));
    return user;
  } catch (err) {
    alert(err.message);
    throw err;
  }
}

// Function to protect a page
function protectPage(requiredRole) {
  if (!currentUser || !token) {
    // Not logged in
    window.location.href = "login.html";
    return;
  }

  if (requiredRole && currentUser.role !== requiredRole) {
    // Logged in but wrong role
    window.location.href = "login.html";
  }
}

// Function to get auth headers for API calls
function getAuthHeaders() {
  const token = localStorage.getItem("edutrack_token");
  return {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json",
  };
}

// Function to logout
function logout() {
  localStorage.removeItem("aamsCurrentUser");
  localStorage.removeItem("edutrack_token");
  window.location.href = "login.html";
}
