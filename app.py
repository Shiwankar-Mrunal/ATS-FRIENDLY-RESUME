from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import PyPDF2
# import docx
import re
import os
import json 
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
SKILLS_FOLDER = "skills"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- HELPERS ----------------

def extract_text(file_path, file_type):
    text = ""
    if file_type == "pdf":
        with open(file_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
    # elif file_type == "docx":
    #     doc = docx.Document(file_path)
    #     for para in doc.paragraphs:
    #         text += para.text + "\n"
    return text


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_experience(resume_text):
    pattern = r"(\d+)\s*\+?\s*(?:years?|yrs?)(?:\s*of\s*experience)?"
    matches = re.findall(pattern, resume_text.lower())
    return max(map(int, matches)) if matches else 0


def load_role_skills(role):
    # Validate role to avoid directory traversal or unsafe characters
    # Allow only letters, numbers, spaces, underscores, and hyphens
    if not re.fullmatch(r"[A-Za-z0-9 _-]+", str(role)):
        return []

    filename = f"{role.lower().replace(' ', '_')}.json"

    # Build an absolute, normalized path under SKILLS_FOLDER
    skills_root = os.path.realpath(SKILLS_FOLDER)
    file_path = os.path.realpath(os.path.join(skills_root, filename))

    # Ensure the resolved path is inside the skills directory
    if os.path.commonpath([skills_root, file_path]) != skills_root:
        return []

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f).get("skills", [])
    return []


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


# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/job_seeker_result")
def job_seeker_result():
    return render_template("job_seeker_result.html")


@app.route("/hiring_manager_result")
def hiring_manager_result():
    return render_template("hiring_manager.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


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


if __name__ == "__main__":
    app.run(debug=True)
