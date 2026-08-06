const loginForm = document.getElementById("loginForm");

loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    try {
        // NOTE: FastAPI's OAuth2PasswordRequestForm expects
        // application/x-www-form-urlencoded with a "username" field
        // (even though we're using it as an email) - not JSON.
        const res = await fetch(API_BASE + "/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ username: email, password: password }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || "Invalid email or password");
        }

        const data = await res.json();

        localStorage.setItem("token", data.access_token);
        localStorage.setItem("role", data.role);
        localStorage.setItem("userName", data.name);

        alert("✅ Login Successful! Welcome, " + data.name + ".");

        if (data.role === "admin") {
            window.location.href = "admin.html";
        } else {
            window.location.href = "index.html";
        }
    } catch (err) {
        alert("❌ " + err.message);
        document.getElementById("password").value = "";
        document.getElementById("password").focus();
    }
});
