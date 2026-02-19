// Store selected technical role globally
window.selectedRole = "";

/* ==============================
   SELECT ROLE BUTTON FUNCTION
============================== */
function selectRole(role) {
    window.selectedRole = role;

    const resultDiv = document.getElementById("result");
    if (resultDiv) {
        resultDiv.innerHTML = `
            <div class="result-card">
                <h3 style="justify-content: center; text-align: center; color: #240680; font-size: 40px; font-weight: bold;">Selected Role</h3>
                <p style="color: #c4380d; font-size: 30px; font-weight: bold; justify-content: center; text-align: center;">${role}</p>
            </div>
        `;
    }
}

/* ==============================
   UPLOAD & SCAN RESUME
============================== */
async function uploadResume(userType) {
    const fileInput = document.getElementById("resumeFile");

    if (!window.selectedRole) {
        alert("Please select a role first.");
        return;
    }

    if (!fileInput || fileInput.files.length === 0) {
        alert("Please upload a resume.");
        return;
    }

    const formData = new FormData();
    formData.append("resume", fileInput.files[0]);
    formData.append("user_type", userType);
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
        if (!response.ok) throw new Error(data.error || "Server error");

        // Save data and role in sessionStorage
        sessionStorage.setItem("scanResult", JSON.stringify(data));
        sessionStorage.setItem("selectedRole", window.selectedRole);

        // Redirect to proper page
        if (userType === "job_seeker") {
            window.location.href = "/job_seeker_result";
        } else if (userType === "hiring_manager") {
            window.location.href = "/hiring_manager_result";
        }

    } catch (error) {
        console.error("Scan Error:", error);
        const resultDiv = document.getElementById("result");
        if (resultDiv) resultDiv.innerHTML = `<p style="color:red;">Error scanning resume</p>`;
    }
}

/* ==============================
   LOAD PREVIOUS RESUMES (HIRING MANAGER)
============================== */
async function loadPreviousResumes() {
    const dropdown = document.getElementById("previousResumeDropdown");
    if (!dropdown) return; // skip if not present

    try {
        const API_BASE_URL =
            window.location.hostname === "127.0.0.1"
                ? "http://127.0.0.1:5000"
                : "https://ats-friendly-resume.onrender.com";

        const response = await fetch(`${API_BASE_URL}/get_uploaded_resumes`);
        const files = await response.json();

        dropdown.innerHTML = `<option value="">Select Previous Resume</option>`;
        files.forEach(file => {
            const option = document.createElement("option");
            option.value = file;
            option.textContent = file;
            dropdown.appendChild(option);
        });

    } catch (error) {
        console.error("Error loading previous resumes:", error);
    }
}

/* ==============================
   SCAN PREVIOUS RESUME
============================== */
async function scanPreviousResume() {
    const filename = document.getElementById("previousResumeDropdown").value;

    if (!window.selectedRole) {
        alert("Please select a role first.");
        return;
    }

    if (!filename) {
        alert("Please select a resume.");
        return;
    }

    try {
        const API_BASE_URL =
            window.location.hostname === "127.0.0.1"
                ? "http://127.0.0.1:5000"
                : "https://ats-friendly-resume.onrender.com";

        const response = await fetch(`${API_BASE_URL}/scan_existing_resume`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                filename: filename,
                selected_role: window.selectedRole
            })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Server error");

        // Save data and redirect to hiring manager result page
        sessionStorage.setItem("scanResult", JSON.stringify(data));
        sessionStorage.setItem("selectedRole", window.selectedRole);
        window.location.href = "/hiring_manager_result";

    } catch (error) {
        console.error("Error scanning previous resume:", error);
        const resultDiv = document.getElementById("result");
        if (resultDiv) resultDiv.innerHTML = `<p style="color:red;">Error scanning resume</p>`;
    }
}

/* ==============================
   AUTO LOAD DROPDOWN ON PAGE LOAD
============================== */
document.addEventListener("DOMContentLoaded", function () {
    loadPreviousResumes();
});
