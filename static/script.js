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
            <p style="color: #00b300; font-weight: bold;">${role}</strong></p>
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
    formData.append("user_type", userType); // job_seeker / hiring_manager
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
============================= */
function displayResult(data, userType) {
    const resultDiv = document.getElementById("result");

    // -------- COMMON RESULT --------
    let html = `
        <div class="result-card">
            <h3>ATS Score</h3>
            <p><strong>${data.ats_score || 0}%</strong></p>
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

        // Show feedback card
        html += `
            <div class="result-card">
                <h3>Feedback</h3>
                <p style="color: #00b300; font-weight: bold;">${feedbackMessage}</p>
            </div>
        `;

        // Show Missing Skills or Perfect Match message
        if ((data.missing_skills || []).length === 0) {
            html += `
                <div class="result-card">
                    <h3>Missing Skills</h3>
                    <p style="color: #00b300; font-weight: bold;">
                        🎉 Congratulations! All required skills matched! 100% skills matched!
                    </p>
                </div>
            `;
        } else {
            html += `
                <div class="result-card">
                    <h3 style="color: #00b300; font-weight: bold;">Missing Skills</h3>
                    <ul>
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

        // Determine hiring decision
        let decision = data.hiring_decision || "";

        html += `
            <div class="result-card">
                <h3>Hiring Decision</h3>
                <p><strong>${decision}</strong></p>
            </div>

            <div class="result-card">
                <h3>Matched Skills</h3>
                <ul>
                    ${matchedSkills.map(skill => `<li style="color: green;">${skill}</li>`).join("")}
                </ul>
            </div>
        `;

        // Missing skills card: show congratulatory message if all matched
        if (mismatchedSkills.length === 0 && matchedSkills.length > 0) {
            html += `
                <div class="result-card">
                    <h3>Missing Skills</h3>
                    <p style="color: #00b300; font-weight: bold;">
                        🎉 Congratulations! All required skills matched! 100% skills matched!
                    </p>
                </div>
            `;
        } else {
            html += `
                <div class="result-card">
                    <h3>Missing Skills</h3>
                    <ul>
                        ${mismatchedSkills.map(skill => `<li style="color: red;">${skill}</li>`).join("")}
                    </ul>
                </div>
            `;
        }

        html += `
            <div class="result-card">
                <h3>Experience</h3>
                <p>${data.experience_years || 0} years</p>
            </div>
        `;
    }

    // Render final HTML
    resultDiv.innerHTML = html;
}

