const registerForm = document.getElementById("registerForm");

registerForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    try {
        await apiFetch("/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, password }),
        });

        alert("✅ Account created! Please login.");
        window.location.href = "login.html";
    } catch (err) {
        alert("❌ Registration failed: " + err.message);
    }
});
