async function uploadResume(role) {
    const fileInput = document.getElementById('resumeFile');
    const jobDesc = document.getElementById('jobDescription').value;
    const resultDiv = document.getElementById('result');

    if (fileInput.files.length === 0 || jobDesc.trim() === "") {
        alert("Please upload resume and paste job description");
        return;
    }

    resultDiv.innerHTML = `<p>Scanning as ${role.replace('_', ' ')}...</p>`;

    const formData = new FormData();
    formData.append("resume", fileInput.files[0]);
    formData.append("job_description", jobDesc);
    formData.append("role", role);

    try {
        const response = await fetch("http://127.0.0.1:5000/scan", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        displayResult(data, role);

    } catch {
        resultDiv.innerHTML = `<p style="color:red;">Error scanning resume</p>`;
    }
}

function displayResult(data, role) {

    let feedbackHTML = "";
    let missingSkillsHTML = "";
    let decisionHTML = "";
    let experienceHTML = "";
    let strengthHTML = "";
    let weaknessHTML = "";

    if (role === "job_seeker") {
        feedbackHTML = `
            <div class="result-card">
                <h3>Feedback</h3>
                <p>${data.feedback}</p>
            </div>
        `;

        missingSkillsHTML = `
            <div class="result-card">
                <h3>Missing Skills</h3>
                <ul>
                    ${data.missing_skills.map(skill => `<li>${skill}</li>`).join("")}
                </ul>
            </div>
        `;
    }

    if (role === "hiring_manager") {

        decisionHTML = `
            <div class="result-card">
                <h3>Hiring Decision</h3>
                <p><strong>${data.decision}</strong></p>
            </div>
        `;

        experienceHTML = `
            <div class="result-card">
                <h3>Experience</h3>
                <p>${data.experience_years} years</p>
            </div>
        `;

        strengthHTML = `
            <div class="result-card">
                <h3>Strengths</h3>
                <ul>
                    ${data.strengths.map(s => `<li>${s}</li>`).join("")}
                </ul>
            </div>
        `;

        weaknessHTML = `
            <div class="result-card">
                <h3>Weaknesses</h3>
                <ul>
                    ${data.weaknesses.map(w => `<li>${w}</li>`).join("")}
                </ul>
            </div>
        `;
    }

    document.getElementById('result').innerHTML = `
        <div class="result-card">
            <h2>${role === "job_seeker" ? "Job Seeker ATS Analysis" : "Hiring Manager Resume Evaluation"}</h2>
        </div>

        <div class="result-card">
            <h3>ATS Score</h3>
            <p><strong>${data.ats_score}%</strong></p>
        </div>

        ${experienceHTML}
        ${decisionHTML}
        ${feedbackHTML}
        ${strengthHTML}
        ${weaknessHTML}
        ${missingSkillsHTML}
    `;
}

