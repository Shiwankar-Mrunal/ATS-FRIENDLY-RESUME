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
    text = re.sub(r'[^a-z\s]', ' ', text)
    return text


def extract_experience(resume_text):
    matches = re.findall(r'(\d+)\s*\+?\s*years?', resume_text.lower())
    return max(map(int, matches)) if matches else 0


def extract_keywords(text, top_n=20):
    """
    Extract important keywords from job description using TF-IDF
    """
    vectorizer = TfidfVectorizer(stop_words='english', max_features=top_n)
    vectorizer.fit([text])
    return vectorizer.get_feature_names_out()


def calculate_ats_score(resume_text, job_desc):
    try:
        # -------- CONTENT SIMILARITY (70%) --------
        vectorizer = TfidfVectorizer(stop_words='english')

        if not resume_text.strip() or not job_desc.strip():
            return 0, [], []

        vectors = vectorizer.fit_transform([resume_text, job_desc])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        content_score = similarity * 70

        # -------- KEYWORD MATCH (30%) --------
        keyword_vectorizer = TfidfVectorizer(stop_words='english', max_features=20)
        keyword_vectorizer.fit([job_desc])
        jd_keywords = keyword_vectorizer.get_feature_names_out()

        matched_keywords = [word for word in jd_keywords if word in resume_text]

        if len(jd_keywords) > 0:
            keyword_score = (len(matched_keywords) / len(jd_keywords)) * 30
        else:
            keyword_score = 0

        total_score = round(content_score + keyword_score, 2)

        return total_score, matched_keywords, list(jd_keywords)

    except Exception as e:
        print("ATS Calculation Error:", str(e))
        return 0, [], []



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
        return jsonify({"error": "Missing resume or job description"}), 400

    # Save file
    filepath = os.path.join(UPLOAD_FOLDER, resume.filename)
    resume.save(filepath)

    # Extract text
    file_type = resume.filename.split('.')[-1].lower()
    resume_text = extract_text(filepath, file_type)

    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(job_desc)

    # Calculate ATS score
    ats_score, matched_keywords, jd_keywords = calculate_ats_score(resume_clean, jd_clean)

    missing_keywords = list(set(jd_keywords) - set(matched_keywords))

    response = {
        "ats_score": ats_score
    }

    # -------- JOB SEEKER --------
    if role == "job_seeker":

        if ats_score < 30:
            feedback = "Low ATS score. Improve resume with more relevant keywords from job description."
        elif ats_score < 50:
            feedback = "Moderate ATS score. Add missing skills and improve alignment."
        else:
            feedback = "Excellent ATS score. Resume matches well with job description."

        response.update({
            "feedback": feedback,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords
        })

    # -------- HIRING MANAGER --------
    if role == "hiring_manager":

        experience = extract_experience(resume_text)

        response.update({
            "experience_years": experience,
            "strengths": matched_keywords,
            "weaknesses": missing_keywords
        })

        if ats_score >= 50:
            decision = "Strong candidate - Shortlist"
        elif ats_score >= 30:
            decision = "Average candidate - Take Interview and then decide"
        else:
            decision = "Weak candidate - Reject"

        response["decision"] = decision

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
