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
            <h3 style="justify-content: center; text-align: center; color: #240680; font-size: 40px; font-weight: bold;">Selected Role</h3>
            <p style="color: #c4380d; font-size: 30px; font-weight: bold; justify-content: center; text-align: center;">${role}</p>
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

        if (!response.ok) {
            throw new Error(data.error || "Server error");
        }

        displayResult(data, userType);

        // Reload dropdown after new upload
        loadPreviousResumes();

    } catch (error) {
        console.error("Scan Error:", error);
        resultDiv.innerHTML = `<p style="color:red;">Error scanning resume</p>`;
    }
}


/* ==============================
   LOAD PREVIOUS RESUMES (HIRING MANAGER)
============================== */
async function loadPreviousResumes() {

    const dropdown = document.getElementById("previousResumeDropdown");
    if (!dropdown) return; // prevent error if not present

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
    const resultDiv = document.getElementById("result");

    if (!window.selectedRole) {
        alert("Please select a role first.");
        return;
    }

    if (!filename) {
        alert("Please select a resume.");
        return;
    }

    resultDiv.innerHTML = `<p>Scanning previous resume...</p>`;

    try {
        const API_BASE_URL =
            window.location.hostname === "127.0.0.1"
                ? "http://127.0.0.1:5000"
                : "https://ats-friendly-resume.onrender.com";

        const response = await fetch(`${API_BASE_URL}/scan_existing_resume`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                filename: filename,
                selected_role: window.selectedRole
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Server error");
        }

        displayResult(data, "hiring_manager");

    } catch (error) {
        console.error("Error scanning previous resume:", error);
        resultDiv.innerHTML = `<p style="color:red;">Error scanning resume</p>`;
    }
}


/* ==============================
   DISPLAY RESULT
============================= */
function displayResult(data, userType) {

    const resultDiv = document.getElementById("result");

    let html = `
        <div class="result-card">
            <h3>ATS Score</h3>
            <p style="color:#0012b3; font-weight: bold;">${data.ats_score || 0}%</p>
            
        </div>
    `;

    /* ==============================
       JOB SEEKER VIEW
    ============================== */
    if (userType === "job_seeker") {

        let feedbackMessage = "";
        const score = data.ats_score || 0;

        if (score >= 90) {
            feedbackMessage = "Excellent match! Your resume is well aligned with this role.";
        } else if (score >= 70) {
            feedbackMessage = "Good profile, but you can improve by adding missing skills.";
        } else if (score >= 40) {
            feedbackMessage = "Your resume needs improvement for this role.";
        } else {
            feedbackMessage = "Your resume is not suitable for this role.";
        }

        html += `
            <div class="result-card">
                <h3>Feedback</h3>
                <p style="color: #00b300; font-weight: bold;">${feedbackMessage}</p>
            </div>
        `;

        if ((data.missing_skills || []).length === 0) {
            html += `
                <div class="result-card">
                    <h3>Missing Skills</h3>
                    <p style="color: #ee3514; font-weight: bold;">
                        🎉 Congratulations! All required skills matched!
                    </p>
                </div>
            `;
        } else {
            html += `
                <div class="result-card">
                    <h3>Missing Skills</h3>
                    <ul style="color: red; font-weight: bold;">
                        ${(data.missing_skills || []).map(skill => `<li>${skill}</li>`).join("")}
                    </ul>
                </div>
            `;
        }
    }

    /* ==============================
   HIRING MANAGER VIEW
============================== */
if (userType === "hiring_manager") {

    const matchedSkills = data.matched_skills || [];
    const mismatchedSkills = data.missing_skills || [];

    html += `
        <div class="result-card">
            <h3>Hiring Decision</h3>
            <p style="color: #ee3514; font-weight: bold;">
                ${data.hiring_decision || ""}
            </p>
        </div>

        <div class="result-card">
            <h3>Matched Skills</h3>
            <ul style="font-weight: bold;">
                ${matchedSkills.map(skill => 
                    `<li style="color: #00b300;">${skill}</li>`
                ).join("")}
            </ul>
        </div>
    `;

    if (mismatchedSkills.length === 0 && matchedSkills.length > 0) {
        html += `
            <div class="result-card">
                <h3>Missing Skills</h3>
                <p style="color: #ee3514; font-weight: bold;">
                    Congratulations! All required skills matched!
                </p>
            </div>
        `;
    } else {
        html += `
            <div class="result-card">
                <h3>Missing Skills</h3>
                <ul style="font-weight: bold;">
                    ${mismatchedSkills.map(skill => 
                        `<li style="color: red;">${skill}</li>`
                    ).join("")}
                </ul>
            </div>
        `;
    }

    html += `
        <div class="result-card">
            <h3>Experience</h3>
            <p style="color: #30d430; font-weight: bold;">
                ${data.experience_years || 0} years
            </p>
        </div>
    `;

    // ✅ NEW: Resume URL Section
    if (data.resume_url) {
        html += `
            <div class="result-card">
                <h3>View Resume</h3>
                <a href="${data.resume_url}" target="_blank"
                   style="color: #0012b3; font-weight: bold; text-decoration: underline;">
                   Click here to open resume
                </a>
            </div>
        `;
    }
}

    resultDiv.innerHTML = html;
}


/* ==============================
   AUTO LOAD DROPDOWN ON PAGE LOAD
============================== */
document.addEventListener("DOMContentLoaded", function () {
    loadPreviousResumes();
});
