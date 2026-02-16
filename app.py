from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import PyPDF2
import docx
import re
import os
import json

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
SKILLS_FOLDER = 'skills'   # Folder containing role JSON files

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    print("🧹 Cleaned Text Preview:", text[:200])
    return text


def extract_experience(resume_text):
    matches = re.findall(r'(\d+)\s*\+?\s*years?', resume_text.lower())
    print(" Resume Text Preview:", resume_text[:200])  # first 200 characters
    return max(map(int, matches)) if matches else 0



def load_role_skills(role):
    """
    Load skills from JSON file based on selected role.
    Example:
    Python Developer -> skills/python_developer.json
    """
    filename = f"{role.lower().replace(' ', '_')}.json"
    file_path = os.path.join(SKILLS_FOLDER, filename)

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get("skills", [])

    return []

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)  # collapse multiple spaces
    return text.strip()


def calculate_ats_score(resume_text, role_skills):
    """
    Compare resume ONLY with role skills.
    Score is 100% based on skill match.
    """
    resume_text = normalize_text(resume_text)

    if not role_skills:
        print("⚠️ No skills loaded for this role!")
        return 0, [], []

    matched_skills = []
    missing_skills = []

    for skill in role_skills:
        skill_norm = normalize_text(skill)
        # Match whole words only
        if re.search(r'\b' + re.escape(skill_norm) + r'\b', resume_text):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    score = (len(matched_skills) / len(role_skills)) * 100
    total_score = round(score, 2)

    print(f"✅ Matched Skills: {matched_skills}")
    print(f"❌ Missing Skills: {missing_skills}")
    print(f"🎯 ATS Score: {total_score}%")

    return total_score, matched_skills, missing_skills



# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan_resume():
    resume = request.files.get("resume")
    user_type = request.form.get("user_type", "")          # job_seeker / hiring_manager
    selected_role = request.form.get("selected_role", "")  # python_developer etc.

    if not resume or not user_type or not selected_role:
        return jsonify({"error": "Missing resume, user type or role"}), 400

    # Save uploaded resume
    filepath = os.path.join(UPLOAD_FOLDER, resume.filename)
    resume.save(filepath)

    # Extract text
    file_type = resume.filename.split('.')[-1].lower()
    resume_text = extract_text(filepath, file_type)
    resume_clean = clean_text(resume_text)

    # Load skills for selected role
    role_skills = load_role_skills(selected_role)

# Terminal output
    if role_skills:
        print(f"📌 Loaded skills for role '{selected_role}': {role_skills}")
    else:
        print(f"⚠️ No skills loaded for role '{selected_role}'!")

    # Calculate ATS based ONLY on role skills
    ats_score, matched_skills, missing_skills = calculate_ats_score(
        resume_clean,
        role_skills
    )

    response = {
        "ats_score": ats_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }

    
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)