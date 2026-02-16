// Store selected technical role globally
window.selectedRole = "";

/* ==============================
   SELECT ROLE BUTTON FUNCTION
============================== */
function selectRole(role) {

    window.selectedRole = role;

    const resultDiv = document.getElementById("result");

    resultDiv.innerHTML = `
        <div class="result-card">
            <h3>Selected Role</h3>
            <p><strong>${role}</strong></p>
        </div>
    `;
}


/* ==============================
   UPLOAD & SCAN RESUME
============================== */
async function uploadResume(userType) {

    const fileInput = document.getElementById("resumeFile");
    const resultDiv = document.getElementById("result");

    if (!window.selectedRole) {
        alert("Please select a role first.");
        return;
    }

    if (fileInput.files.length === 0) {
        alert("Please upload a resume.");
        return;
    }

    resultDiv.innerHTML = `<p>Scanning resume...</p>`;

    const formData = new FormData();
    formData.append("resume", fileInput.files[0]);
    formData.append("user_type", userType);             // job_seeker / hiring_manager
    formData.append("selected_role", window.selectedRole);

    try {

        const API_BASE_URL =
            window.location.hostname === "127.0.0.1"
                ? "http://127.0.0.1:5000"
                : "https://ats-friendly-resume.onrender.com";

        const response = await fetch(`${API_BASE_URL}/scan`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Server error");
        }

        displayResult(data, userType);

    } catch (error) {
        console.error("Scan Error:", error);
        resultDiv.innerHTML = `<p style="color:red;">Error scanning resume</p>`;
    }
}


/* ==============================
   DISPLAY RESULT
============================== */
function displayResult(data, userType) {


    // -------- COMMON RESULT --------
    document.getElementById("result").innerHTML = `

        <div class="result-card">
            <h3>ATS Score</h3>
            <p><strong>${data.ats_score || 0}%</strong></p>
        </div>
    `;
}
