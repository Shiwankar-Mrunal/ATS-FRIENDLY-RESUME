from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import PyPDF2
import docx
import re
import os
import json

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
SKILLS_FOLDER = 'skills'

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
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_experience(resume_text):
    resume_text = resume_text.lower()
    pattern = r'(\d+)\s*\+?\s*(?:years?|yrs?)(?:\s*of\s*experience)?'
    matches = re.findall(pattern, resume_text)
    if matches:
        return max(map(int, matches))
    return 0


def load_role_skills(role):
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
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


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


def process_resume(filepath, selected_role, user_type):
    file_type = filepath.split('.')[-1].lower()

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


# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return render_template("index.html")


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


# ✅ NEW: Get all uploaded resumes
@app.route("/get_uploaded_resumes")
def get_uploaded_resumes():
    files = [f for f in os.listdir(UPLOAD_FOLDER)
             if f.endswith(('.pdf', '.docx'))]
    return jsonify(files)


# ✅ NEW: Scan existing resume from uploads folder
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


if __name__ == "__main__":
    app.run(debug=True)
