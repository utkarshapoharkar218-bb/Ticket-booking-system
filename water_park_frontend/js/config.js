// ============================================
// Central place for the backend API URL.
// Change this if your FastAPI server runs somewhere else.
// ============================================
const API_BASE = "http://127.0.0.1:8000";

// ---- small shared helpers used by every page ----

function getToken() {
    return localStorage.getItem("token");
}

function getRole() {
    return localStorage.getItem("role");
}

function getUserName() {
    return localStorage.getItem("userName");
}

function isLoggedIn() {
    return !!getToken();
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("userName");
    window.location.href = "login.html";
}

// Redirects to login.html if there's no token. Call this at the top of
// any page that requires the user to be logged in (booking, food, stay).
function requireLogin() {
    if (!isLoggedIn()) {
        alert("Please login first.");
        window.location.href = "login.html";
    }
}

// Redirects to login.html if there's no token, or home if logged in but not an admin.
function requireAdmin() {
    if (!isLoggedIn()) {
        alert("Please login first.");
        window.location.href = "login.html";
        return;
    }
    if (getRole() !== "admin") {
        alert("Admin access only.");
        window.location.href = "index.html";
    }
}

// Wrapper around fetch() that automatically attaches the JWT token
// and throws a readable error if the API returns a non-2xx response.
async function apiFetch(path, options = {}) {
    const headers = options.headers || {};
    if (getToken()) {
        headers["Authorization"] = "Bearer " + getToken();
    }
    const res = await fetch(API_BASE + path, { ...options, headers });

    if (!res.ok) {
        let detail = "Something went wrong.";
        try {
            const errBody = await res.json();
            detail = errBody.detail || detail;
        } catch (e) {
            /* ignore parse errors */
        }
        throw new Error(detail);
    }

    // some endpoints (like DELETE) may return no content
    const text = await res.text();
    return text ? JSON.parse(text) : null;
}
