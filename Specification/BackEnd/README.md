#  1.4 "***How Backend will work***"

### "***app.py***" 
# 1. Imports and App Initialization : 
-   Flask – the main web framework.
-   request, jsonify, render_template, send_from_directory – for handling HTTP requests, sending JSON responses, rendering HTML templates, and serving uploaded files.
-   CORS – Cross-Origin Resource Sharing; allows frontend (maybe React or another web client) to call the Flask API from a different origin.
- PyPDF2 – for reading text from PDF files.
- re – regular expressions for text cleaning and pattern matching.
- os – file system operations.
- json – reading JSON files containing skills for roles.
- from werkzeug.utils import secure_filename - Prevents security risks when saving uploaded files. 

```
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import PyPDF2
import re
import os
import json
from werkzeug.utils import secure_filename
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

-  Detects file type (pdf) and extracts text from the file.
```
def extract_text(file_path, file_type):
    text = ""

    if file_type == 'pdf':
        with open(file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"

    return text
```

### b) Normalized text

- Converts text to lowercase.
- Removes all special characters.
- Replaces multiple spaces with a single space.
- Returns clean, normalized text for analysis.

```
def normalize_text(text):
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
    pattern = r"(\d+)\s*\+?\s*(?:years?|yrs?)(?:\s*of\s*experience)?"
    matches = re.findall(pattern, resume_text.lower())
    return max(map(int, matches)) if matches else 0
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
        with open(file_path, "r") as f:
            return json.load(f).get("skills", [])
    return []
```

<!-- ### e) Normalize text

- Similar to clean_text but used specifically for matching skills.
- Ensures consistency when checking if a skill is mentioned in resume.

```
def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
``` -->



### f) Calculate ATS score

- Checks if each skill is present in the resume.
- Calculates ATS score : Percentage of required skills found in resume.
- Returns:

    - ```total_score``` – ATS score

    - ```matched_skills```  – skills found in resume

    - ```missing_skills``` – skills not found in resume

```
def calculate_ats_score(resume_text, role_skills):
    resume_text = normalize_text(resume_text)
    matched_skills = []
    missing_skills = []

    for skill in role_skills:
        if re.search(r"\b" + re.escape(normalize_text(skill)) + r"\b", resume_text):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    score = round((len(matched_skills) / len(role_skills)) * 100, 2) if role_skills else 0
    return score, matched_skills, missing_skills

```
### g) process_resume

The function processes a resume file for a selected role and user type.


- Extracts the file type and reads text from the resume.
- Extracts years of experience from the resume text.
- Loads role-specific skills.
- Calculates ATS score, matched skills, and missing skills.
- Builds a response dictionary containing ats_score, matched_skills, missing_skills, and experience_years.

If user_type is "hiring_manager", adds a hiring_decision based on the number of matched skills.

- Inputs: filepath, selected_role, user_type
- Outputs: Response dictionary with ATS results, experience, and optionally a hiring decision.
Note: The function does not currently return perfect_match_message or resume URL.

```
def process_resume(filepath, selected_role, user_type):
    file_type = filepath.split(".")[-1].lower()
    resume_text = extract_text(filepath, file_type)
    experience = extract_experience(resume_text)

    role_skills = load_role_skills(selected_role)
    ats_score, matched_skills, missing_skills = calculate_ats_score(resume_text, role_skills)

    response = {
        "ats_score": ats_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "experience_years": experience
    }

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

    return response
```

# 4. Routes
### a) Home page
- Loads a web page (index.html) for the index.html.
```
@app.route("/")
def index():
    return render_template("index.html")
```
- Loads a web page (index.html) for the job job_seeker_result.html
```
@app.route("/job_seeker_result")
def job_seeker_result():
    return render_template("job_seeker_result.html")
```

- Loads a web page (index.html) for the hiring_manager.html
```
@app.route("/hiring_manager_result")
def hiring_manager_result():
    return render_template("hiring_manager.html")
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
- call process_resume function and return JSON result.

```
@app.route("/scan", methods=["POST"])
def scan_resume():
    resume = request.files.get("resume")
    user_type = request.form.get("user_type")
    selected_role = request.form.get("selected_role")

    if not resume or not user_type or not selected_role:
        return jsonify({"error": "Missing resume, user type, or role"}), 400

    filename = secure_filename(resume.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    resume.save(path)

    result = process_resume(path, selected_role, user_type)
    result["resume_url"] = f"/uploads/{filename}"
    result["resume_text"] = extract_text(path, filename.split(".")[-1].lower())
    return jsonify(result)
```


### d) Run the app

- Runs the Flask development server with debugging enabled.
- By default, it runs on http://localhost:5000.

```
if __name__ == "__main__":
    app.run(debug=True)
```