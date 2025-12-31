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
    return round(similarity * 100, 2)  # 0–100


def keyword_match_score(resume_text, job_desc):
    resume_words = set(resume_text.split())
    jd_words = set(job_desc.split())

    matched = resume_words.intersection(jd_words)
    if not jd_words:
        return 0

    return round((len(matched) / len(jd_words)) * 100, 2)  # 0–100


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

    if job_desc.strip() == "":
        return jsonify({"error": "Job description missing"}), 400

    filename = os.path.join(UPLOAD_FOLDER, resume.filename)
    resume.save(filename)

    file_type = resume.filename.split('.')[-1].lower()
    if file_type not in ['pdf', 'docx']:
        return jsonify({"error": "Unsupported file format"}), 400

    resume_text = extract_text(filename, file_type)

    # Clean texts
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(job_desc)

    # NLP Scores (0–100)
    similarity_score = calculate_similarity(resume_clean, jd_clean)
    keyword_score = keyword_match_score(resume_clean, jd_clean)

    # ✅ FINAL ATS SCORE (EXPLICITLY IN TERMS OF 100)
    ats_score = round(
        ((similarity_score / 100) * 0.7 +
         (keyword_score / 100) * 0.3) * 100,
        2
    )

    return jsonify({
        "similarity_score": similarity_score,
        "keyword_score": keyword_score,
        "ats_score": ats_score
    })


if __name__ == "__main__":
    app.run(debug=True)
