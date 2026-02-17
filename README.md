#  ATS Resume Scanner (Applicant Tracking System Resume Analyzer)

- An ATS Resume Scanner automatically analyzes and parses resumes using predefined rules and NLP techniques.

- It compares resume content with job descriptions to calculate ATS Scores

- The system helps recruiters efficiently shortlist the most relevant candidates with fair and consistent screening.

## Objectives 

- Automate resume screening and candidate shortlisting using ATS logic

- Extract structured data from unstructured resume formats (PDF, DOCX)

- Match resumes with job descriptions using keyword

- Generate relevance-based match scores for each resume

- Rank candidates to support faster recruiter decision-making

- Scale efficiently to process large volumes of resumes

## Problem Statement 

- Recruiters receive a very large number of resumes for each job opening, making manual screening inefficient.

- Manual resume review is time-consuming, inconsistent, and can introduce bias.

- Many qualified candidates are rejected due to poor ATS optimization of resumes.

- There is a need for an automated system to parse resumes and extract key details such as skills, experience, and education.

- Matching resumes with job descriptions and generating suitability scores can improve hiring efficiency and consistency.

## Steps to achieve the targeted goal

- Create Frotend using html css 
- Use Javascript to make page interactive and add functionality.
- Work on backend by using flask to calculate ats score
- There are two button 
    - For Job Seeker 
        - Ats Score
        - Feedback
        - Missing Skills

    - For Highring Manager
        - Ats Score
        - Experience
        - Decision Of Highring
        - Strength
        - Weaknesses

# Detail Workflow

## 1.1 Folder Structure : 


    ```
    ATS-Resume-Scanner/
    │
    ├── Diagram/
    │   └── ATS-Resume.png
    │
    ├── docs/
    │   └── index.html
    │
    ├── skills/
    │   ├── developer.json
    │   ├── devops.json
    │   ├── sap.json
    │   ├── socanalyst.json
    │   ├── sre.json
    │   └── tester.json
    │
    ├── static/
    │   ├── script.js
    │   └── style.css
    │
    ├── templates/
    │   └── index.html
    │
    ├── uploads/
    │   ├── (Uploaded Resume PDFs)
    │
    ├── app.py
    ├── requirements.txt
    └── README.md

    ```

## 1.2 Front End  

### Inside this project main focus is on following role : 

- Python developer
- Automation tester
- SAP
- SRE
- DevOps
- SocAnalyst

### Step 1:  Please  choose the role first.

### Step 2: Choose File PDF/DOCX

### Step 3: Select option according to need

    - Scan as Job Seeker
    - Scan as Hiring Manager


![alt text](image.png)



## 1.3 Scenario After selecting any role  " ***DevOPs*** "

- After selecting role please choose resume PDF

![alt text](image-1.png)

- After this user have two options

    - If you are Job Seeker select   ``` Scan as JOB SEEKER ```
    - If You are Hiring Manager select ``` Scan as HIRING MANAGER```


#  1.4 "***How Backend will work***"

### "***app.py***" 

# 1. Imports and App Initialization : 

-   Flask – the main web framework.

-   request, jsonify, render_template, send_from_directory – for handling HTTP requests, sending JSON responses, rendering HTML templates, and serving uploaded files.

-   CORS – Cross-Origin Resource Sharing; allows frontend (maybe React or another web client) to call the Flask API from a different origin.

- PyPDF2 – for reading text from PDF files.

- docx – for reading Microsoft Word documents.

- re – regular expressions for text cleaning and pattern matching.

- os – file system operations.

- json – reading JSON files containing skills for roles.

```from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import PyPDF2
import docx
import re
import os
import json
```

# 2. App Configuration

-   Initializes Flask app and enables CORS.

-   UPLOAD_FOLDER – directory where uploaded resumes are stored.

-   SKILLS_FOLDER – directory where JSON files defining skills per role are stored.

-   os.makedirs(..., exist_ok=True) ensures the folder exists (creates it if not).

```
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
SKILLS_FOLDER = 'skills'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
```



# 3 . Helper Function : 

- In JavaScript, a helper function is a small, reusable function that performs a specific, often repeated task to support a larger function or program.

- They are not the main logic themselves but are used to make the main function cleaner, more readable, and easier to maintain.

### Key Points about Helper Functions : 


```Purpose```           :   Break down complex logic into smaller, manageable parts.

```Reusability```       :   Can be called from multiple places in your code.

```Readability```       :   Makes the main function shorter and easier to understand.

```Maintainability```   :   If the logic changes, you only update the helper function.


### a) Extract text from resume :

-  Detects file type (pdf or docx) and extracts text from the file.

```
def extract_text(file_path, file_type):
    text = ""

    if file_type == 'pdf':
        with open(file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"

    elif file_type == 'docx':
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    return text
```

### b) Clean text

- Converts text to lowercase.

- Removes all special characters.

- Replaces multiple spaces with a single space.

- Returns clean, normalized text for analysis.

```
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
```

### c) Extract experience

- Looks for phrases like "3 years of experience" or "5 yrs".

- Uses regex to capture numbers before "year/yr".

- Returns the highest number of years found.

```
def extract_experience(resume_text):
    resume_text = resume_text.lower()
    pattern = r'(\d+)\s*\+?\s*(?:years?|yrs?)(?:\s*of\s*experience)?'
    matches = re.findall(pattern, resume_text)
    if matches:
        return max(map(int, matches))
    return 0
```

### d) Load skills for a role

- Converts a role name (like "Data Scientist") to a JSON filename (data_scientist.json).

- Reads skills from the JSON file under skills key.

- Returns a list of required skills for that role.

```
def load_role_skills(role):
    filename = f"{role.lower().replace(' ', '_')}.json"
    file_path = os.path.join(SKILLS_FOLDER, filename)

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get("skills", [])

    return []

```

### e) Normalize text

- Similar to clean_text but used specifically for matching skills.

- Ensures consistency when checking if a skill is mentioned in resume.

```
def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
```

### f) Calculate ATS score

- Checks if each skill is present in the resume.

- Calculates ATS score : Percentage of required skills found in resume.

- Returns:

    - ```total_score``` – ATS score

    - ```matched_skills```  – skills found in resume

    - ```missing_skills``` – skills not found in resume

    - ```perfect_match_message``` – if all skills are matched


```
def calculate_ats_score(resume_text, role_skills):
    resume_text = normalize_text(resume_text)

    if not role_skills:
        return 0, [], [], None

    matched_skills = []
    missing_skills = []

    for skill in role_skills:
        skill_norm = normalize_text(skill)
        if re.search(r'\b' + re.escape(skill_norm) + r'\b', resume_text):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    score = (len(matched_skills) / len(role_skills)) * 100
    total_score = round(score, 2)

    perfect_match_message = None
    if not missing_skills and role_skills:
        perfect_match_message = "🎉 Congratulations! All required skills matched! 100% skills matched!"

    return total_score, matched_skills, missing_skills, perfect_match_message

```

### g) process_resume

- Extract file info
- Extract text, experience, clean text
- Load Role-Specific Skills
- Calculate ATS Score
    - Inputs : 
        - resume_text
        - role_skills
    - Output :
        - ats_score – % of skills matched.

        - matched_skills – Skills found in the resume.

        - missing_skills – Skills not found.

        - perfect_match_message – Message if all skills match.

- Build Base Response.

    - Adds congratulatory message if all skills matched.

- Hiring Manager-Specific Logic
- Make a Hiring Decision
- Provide Resume URL

```
def process_resume(filepath, selected_role, user_type):
    file_type = filepath.split('.')[-1].lower()
    filename = os.path.basename(filepath)

    resume_text = extract_text(filepath, file_type)
    experience_years = extract_experience(resume_text)
    resume_clean = clean_text(resume_text)
    role_skills = load_role_skills(selected_role)

    ats_score, matched_skills, missing_skills, perfect_match_message = calculate_ats_score(
        resume_clean,
        role_skills
    )

    response = {
        "ats_score": ats_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "experience_years": experience_years
    }

    if perfect_match_message:
        response["perfect_match_message"] = perfect_match_message

    # Only for Hiring Manager
    if user_type == "hiring_manager":
        matched_count = len(matched_skills)
        total_skills = len(role_skills)

        if matched_count == total_skills and total_skills > 0:
            decision = "🎉 100% skills matched!"
        elif matched_count >= 8:
            decision = "Strong candidate – Please shortlist"
        elif matched_count >= 5:
            decision = "Average candidate – Can interview"
        else:
            decision = "Do not hire"

        response["hiring_decision"] = decision

        # Resume URL instead of text
        response["resume_url"] = f"http://localhost:5000/uploads/{filename}"

    return response
```

# 4. Routes

### a) Home page

- Loads a web page (index.html) for the frontend.

```
@app.route("/")
def index():
    return render_template("index.html")
```

### b) Serve uploaded files

- Allows downloaded or viewing uploaded resumes via URL.

```@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
```

### c) Scan uploaded resume

- Receives resume via POST method
- Receive input such as
    - selected_role
    - resume
    - user_type
    - If Input no selected error will print 
    
    ```"{"error": "Missing resume, user type or role"}"```

- If all input receive correctly save resume on uploads/ .
- camm process_resume function and return JSON result.

    
```
@app.route("/scan", methods=["POST"])
def scan_resume():
    resume = request.files.get("resume")
    user_type = request.form.get("user_type", "")
    selected_role = request.form.get("selected_role", "")

    if not resume or not user_type or not selected_role:
        return jsonify({"error": "Missing resume, user type or role"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, resume.filename)
    resume.save(filepath)

    response = process_resume(filepath, selected_role, user_type)
    return jsonify(response)
```


### d) List all uploaded resumes

- Returns JSON list of all uploaded PDF/DOCX files.

```
@app.route("/get_uploaded_resumes")
def get_uploaded_resumes():
    files = [f for f in os.listdir(UPLOAD_FOLDER)
             if f.endswith(('.pdf', '.docx'))]
    return jsonify(files)

```

### e)  Scan an existing uploaded resume

- Scans a resume already in the uploads/ folder.

- Used for hiring managers to re-analyze resumes.

```
@app.route("/scan_existing_resume", methods=["POST"])
def scan_existing_resume():
    data = request.json
    filename = data.get("filename")
    selected_role = data.get("selected_role")

    if not filename or not selected_role:
        return jsonify({"error": "Missing filename or role"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    response = process_resume(filepath, selected_role, "hiring_manager")
    return jsonify(response)
```

### f) Run the app

- Runs the Flask development server with debugging enabled.

- By default, it runs on http://localhost:5000.

```
if __name__ == "__main__":
    app.run(debug=True)
```

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
            <p style="color: #00b300; font-weight: bold;">${feedbackMessage}</p>
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
```
- Shows missing skills, or congratulates if all skills are matched.
```
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
```
- Displays experience extracted from resume.
```
    html += `
        <div class="result-card">
            <h3>Experience</h3>
            <p style="color: #30d430; font-weight: bold;">
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
                   style="color: #0012b3; font-weight: bold; text-decoration: underline;">
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
```


# Select Scan as Job Seeker : 

### "***Display***" 
    - ATS Score
    - Feedback for Job Seeker
    - Missing Skills for implevement

![alt text](image-2.png)

# Select Scan as HIRING manager : 

### "***Display***" 

    - Display ATS Score
    - Hiring Decision
    - Matched Skills
    - Missing Skills
    - Experience
    - View Resume
    - Click here to open resume

![alt text](image-3.png)