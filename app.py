from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import PyPDF2
import docx
import re
import os

# NLP
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- HELPER FUNCTIONS ----------------

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
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text


def calculate_similarity(resume_text, job_desc):
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([resume_text, job_desc])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(similarity * 100, 2)


def extract_experience(resume_text):
    # Find patterns like "5 years" or "3+ years"
    matches = re.findall(r'(\d+)\s*\+?\s*years?', resume_text.lower())
    if matches:
        return max(int(m) for m in matches)
    return 0


def get_missing_skills(resume_text, job_desc):
    return sorted(list(set(job_desc.split()) - set(resume_text.split())))

# ---------------- ROUTES ----------------

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400

    resume = request.files['resume']
    job_desc = request.form.get("job_description", "")
    role = request.form.get("role", "job_seeker")

    if job_desc.strip() == "":
        return jsonify({"error": "Job description missing"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, resume.filename)
    resume.save(filepath)

    file_type = resume.filename.split('.')[-1].lower()
    if file_type not in ['pdf', 'docx']:
        return jsonify({"error": "Unsupported file format"}), 400

    resume_text = extract_text(filepath, file_type)
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(job_desc)

    similarity_score = calculate_similarity(resume_clean, jd_clean)

    ats_score = round(
        (similarity_score / 100) * 100,  # Only similarity used now
        2
    )

    response = {
        "similarity_score": similarity_score,
        "ats_score": ats_score
    }

    # -------- JOB SEEKER FEEDBACK --------
    if role == "job_seeker":
        # Feedback based on similarity
        if similarity_score < 20:
            feedback = "Please work on skills"
        elif similarity_score < 50:
            feedback = "Please work a little more on your skills"
        else:
            feedback = "Your skills match well with the job description"

        response["feedback"] = feedback
        response["missing_skills"] = get_missing_skills(resume_clean, jd_clean)

    # -------- HIRING MANAGER DECISION --------
    if role == "hiring_manager":
        response["experience_years"] = extract_experience(resume_text)
        if ats_score > 40:
            response["decision"] = "There is a chance of hiring"
        else:
            response["decision"] = "No chance of hiring"

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
