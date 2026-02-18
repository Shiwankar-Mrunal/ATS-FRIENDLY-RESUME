#  1.5 "***How FrontEnd will work***"
## 1. Global Variables

```
window.selectedRole = "";
```

## 2. Select Role Function

- Updates the selected role.

```
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
```

## 3. Upload & Scan Resume
### Validate Role and File
- A role must be selected (window.selectedRole must not be empty).
- A file must be uploaded.

```
if (!window.selectedRole) {
    alert("Please select a role first.");
    return;
}

if (fileInput.files.length === 0) {
    alert("Please upload a resume.");
    return;
}
```

### Prepare Form Data for Upload

- Adds three pieces of data to send to the backend:
    - "resume" – the uploaded file itself
    - "user_type" – "job_seeker" or "hiring_manager"
    - "selected_role" – the role selected by the user
```
const formData = new FormData();
formData.append("resume", fileInput.files[0]);
formData.append("user_type", userType);
formData.append("selected_role", window.selectedRole);
```

### Determine API Base URL

- Dynamically decides whether to use:
- Local Flask server (http://127.0.0.1:5000) if running locally.
- Deployed server (https://ats-friendly-resume.onrender.com) if in production.

```
const API_BASE_URL =
    window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:5000"
        : "https://ats-friendly-resume.onrender.com";

```
### Send Resume to Backend
```
const response = await fetch(`${API_BASE_URL}/scan`, {
    method: "POST",
    body: formData
});
```

### Process Response
```
const data = await response.json();

if (!response.ok) {
    throw new Error(data.error || "Server error");
}
```

### Display Result
```
displayResult(data, userType);
```
### Reload Previous Resumes Dropdown
```
loadPreviousResumes();
```
### Error Handling

```
catch (error) {
    console.error("Scan Error:", error);
    resultDiv.innerHTML = `<p style="color:red;">Error scanning resume</p>`;
}
```

## 4.Load Previous Resumes (Hiring Manager)

-  loadPreviousResumes is an asynchronous frontend function that fetches the list of previously uploaded resumes from the backend and dynamically fills a dropdown menu for the hiring manager.

```
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
```

## 5. Scan Previous Resume

- Checks that a role and resume are selected.
- Shows "Scanning..." message.

```
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
```

-   Calls /scan_existing_resume endpoint with filename and role.
- Displays result as hiring manager view.

```
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
```

## 6. Display Result

-  Shows ATS score in a card.

```
function displayResult(data, userType) {

    const resultDiv = document.getElementById("result");

    let html = `
        <div class="result-card">
            <h3>ATS Score</h3>
            <p style="color:#0012b3; font-weight: bold;">${data.ats_score || 0}%</p>
        </div>
    `;
```

- Provides feedback messages based on ATS score thresholds.
```
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
```
- Displays feedback message.

```
    html += `
        <div class="result-card">
            <h3>Feedback</h3>
            <p style="color:#00b300; font-weight: bold;">${feedbackMessage}</p>
        </div>
    `;
```
- Shows missing skills if any.

- Congratulatory message if all skills are matched.

```
    if ((data.missing_skills || []).length === 0) {
        html += `
            <div class="result-card">
                <h3>Missing Skills</h3>
                <p style="color:#ee3514; font-weight: bold;">
                     Congratulations! All required skills matched!
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
```

-   Shows hiring decision.

- Lists matched skills in green.

```
if (userType === "hiring_manager") {

    const matchedSkills = data.matched_skills || [];
    const mismatchedSkills = data.missing_skills || [];

    html += `
        <div class="result-card">
            <h3>Hiring Decision</h3>
            <p style="color:#ee3514; font-weight: bold;">
                ${data.hiring_decision || ""}
            </p>
        </div>

        <div class="result-card">
            <h3>Matched Skills</h3>
            <ul style="font-weight: bold;">
                ${matchedSkills.map(skill => 
                    `<li style="color:#00b300;">${skill}</li>`
                ).join("")}
            </ul>
        </div>
    `;
```
- Shows missing skills, or congratulates if all skills are matched.
```
    if (mismatchedSkills.length === 0 && matchedSkills.length > 0) {
        html += `
            <div class="result-card">
                <h3>Missing Skills</h3>
                <p style="color:#ee3514; font-weight: bold;">
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
```
- Displays experience extracted from resume.
```
    html += `
        <div class="result-card">
            <h3>Experience</h3>
            <p style="color:#30d430; font-weight: bold;">
                ${data.experience_years || 0} years
            </p>
        </div>
    `;
```
- Provides link to view resume if URL is available.
```
    if (data.resume_url) {
        html += `
            <div class="result-card">
                <h3>View Resume</h3>
                <a href="${data.resume_url}" target="_blank"
                   style="color:#0012b3; font-weight: bold; text-decoration: underline;">
                   Click here to open resume
                </a>
            </div>
        `;
    }
}
```
- Updates the results container with the generated HTML.

```
   resultDiv.innerHTML = html;

```
- Auto-load Dropdown on Page Load
```
document.addEventListener("DOMContentLoaded", function () {
    loadPreviousResumes();
});