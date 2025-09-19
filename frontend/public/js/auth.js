// public/js/auth.js

const API_URL = "http://localhost:8000/api"; // Adjust if deployed

// Get current logged-in user dynamically
function getCurrentUser() {
  return JSON.parse(localStorage.getItem("aamsCurrentUser"));
}

// Get token dynamically
function getToken() {
  return localStorage.getItem("edutrack_token");
}

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

    // Save token
    localStorage.setItem("edutrack_token", data.access_token);

    // Store minimal user object
    const user = {
      email,
      role: data.role || "student", // adjust if backend sends role differently
      id: data.user_id,
      full_name: data.full_name,
    };

    localStorage.setItem("aamsCurrentUser", JSON.stringify(user));
    return user;
  } catch (err) {
    alert(err.message);
    throw err;
  }
}

// Function to protect a page based on role(s)
function protectPage(requiredRoles) {
  const user = getCurrentUser();
  const token = getToken();

  if (!user || !token) {
    window.location.href = "login.html";
    return;
  }

  if (requiredRoles) {
    if (Array.isArray(requiredRoles)) {
      if (!requiredRoles.includes(user.role)) {
        alert("You do not have permission to access this page.");
        window.location.href = "login.html";
      }
    } else if (user.role !== requiredRoles) {
      alert("You do not have permission to access this page.");
      window.location.href = "login.html";
    }
  }
}

// Function to get auth headers for API calls
function getAuthHeaders() {
  const token = getToken();
  return {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json",
  };
}

// Authenticated fetch wrapper with 401 handling
async function authFetch(input, init = {}) {
  const headers = Object.assign({}, init.headers || {}, getAuthHeaders());
  const opts = Object.assign({}, init, { headers });
  const response = await fetch(input, opts);
  if (response.status === 401) {
    try { logout(); } catch {}
  }
  return response;
}

// Logout function
function logout() {
  localStorage.removeItem("aamsCurrentUser");
  localStorage.removeItem("edutrack_token");
  window.location.href = "login.html";
}
