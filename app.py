
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import PyPDF2
import docx
import re
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- UNIVERSAL SKILLS (150) ----------------
UNIVERSAL_SKILLS = [
    # Software Testing
    "manual testing", "automation testing", "selenium", "cucumber", "test cases",
    
    # Programming Languages
    "python", "java", "c", "c++", "c#", "javascript", "typescript", "ruby", "php", "go",
    

    # Web Development
    "html", "css", "bootstrap", "react", "angular", "vue", "node.js", "express", "django", "flask",
    

    # Databases
    # "sql", "mysql", "postgresql", "oracle", "mongodb", "redis", 
    

    # DevOps / Cloud
    # "docker", "kubernetes", "jenkins", "ci cd", "ansible", "terraform", "aws", "azure", "gcp", "ec2",
    

    # SAP Modules
    "sap mm", "procurement", "purchase order", "inventory management", 

    # Networking / Security
    # "linux", "unix", "windows server", "firewall", "vpn", 

    # Analytics / Data Science
    # "excel", "power bi", "tableau", "qlikview", "data visualization",
    

    # Agile / Project Management
    # "agile", "scrum", "kanban", "sprint", "product backlog",

    # General IT / Soft Skills
    # "documentation", "presentation", "collaboration", "customer support", "troubleshooting",
    
]

# ---------------- HELPERS ----------------

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

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text

def calculate_similarity(resume_text, job_desc):
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([resume_text, job_desc])
    return round(cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100, 2)

def extract_experience(resume_text):
    matches = re.findall(r'(\d+)\s*\+?\s*years?', resume_text.lower())
    return max(map(int, matches)) if matches else 0

def analyze_skills(resume_text):
    matched = []
    missing = []

    for skill in UNIVERSAL_SKILLS:
        if skill in resume_text.lower():
            matched.append(skill)
        else:
            missing.append(skill)

    return matched, missing

# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan_resume():
    resume = request.files.get("resume")
    job_desc = request.form.get("job_description", "")
    role = request.form.get("role")

    if not resume or not job_desc:
        return jsonify({"error": "Missing data"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, resume.filename)
    resume.save(filepath)

    file_type = resume.filename.split('.')[-1].lower()
    resume_text = extract_text(filepath, file_type)

    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(job_desc)

    ats_score = calculate_similarity(resume_clean, jd_clean)

    matched_skills, missing_skills = analyze_skills(resume_text)

    response = {
        "ats_score": ats_score
    }

    # -------- JOB SEEKER --------
    if role == "job_seeker":
        if len(matched_skills) <= 3:
            feedback = "Your resume lacks many required skills. Please work on improving your skills."
        elif len(matched_skills) <= 6:
            feedback = "Partial skill match. Improve remaining skills."
        else:
            feedback = "Good skill match. Your resume is strong."

        response.update({
            "feedback": feedback,
            "missing_skills": missing_skills
        })

    # -------- HIRING MANAGER --------
    if role == "hiring_manager":
        response.update({
            "experience_years": extract_experience(resume_text),
            "strengths": matched_skills,
            "weaknesses": missing_skills
        })

        if len(matched_skills) >= 6:
            response["decision"] = "Strong candidate – shortlist"
        elif len(matched_skills) >= 3:
            response["decision"] = "Average candidate – review"
        else:
            response["decision"] = "Weak candidate – reject"

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
