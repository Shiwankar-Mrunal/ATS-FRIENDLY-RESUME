
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import PyPDF2
import docx
import re
import os

app = Flask(__name__)
CORS(app, origins="*")  # Allow requests from any origin

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure folder exists


# ---------------- HELPER FUNCTIONS ----------------

def extract_text(file_path, file_type):
    """Extract text from PDF or DOCX files"""
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


def parse_resume(text):
    """Parse resume text to extract details"""
    # Extract email & phone
    email = re.findall(r'\S+@\S+', text)
    phone = re.findall(r'\+?\d[\d -]{8,}\d', text)

    # Extract name (first 2 words as heuristic)
    words = text.strip().split()
    name = " ".join(words[0:2]) if len(words) >= 2 else (words[0] if words else "")

    # Skills
    skills_list = [
        "Python", "JavaScript", "HTML", "CSS",
        "Flask", "Django", "Machine Learning", "Data Analysis"
    ]
    skills = [skill for skill in skills_list if skill.lower() in text.lower()]

    # Education
    education_keywords = ["Bachelor", "Master", "B.Sc", "B.E", "M.Sc", "MBA"]
    education = [edu for edu in education_keywords if edu.lower() in text.lower()]

    # Certifications
    cert_keywords = ["AWS", "Azure", "Google Cloud", "PMP", "Scrum", "Cisco"]
    certifications = [cert for cert in cert_keywords if cert.lower() in text.lower()]

    # Experience
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    experience = [
        line for line in lines
        if "experience" in line.lower() or "year" in line.lower()
    ]

    return {
        "name": name,
        "email": email[0] if email else "",
        "phone": phone[0] if phone else "",
        "skills": skills,
        "education": education,
        "certifications": certifications,
        "experience": experience
    }


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/scan", methods=["POST", "OPTIONS"])
def scan_resume():
    """API endpoint to handle resume upload and return extracted details"""
    print("SCAN ENDPOINT HIT")

    if request.method == "OPTIONS":
        return "", 200

    # Check if file is present
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    resume = request.files['resume']
    filename = os.path.join(UPLOAD_FOLDER, resume.filename)
    resume.save(filename)
    print("File received:", resume.filename)

    file_type = filename.split('.')[-1].lower()
    if file_type not in ['pdf', 'docx']:
        return jsonify({"error": "Unsupported file format"}), 400

    # Extract text and parse
    text = extract_text(filename, file_type)
    result = parse_resume(text)

    # Debug prints
    print("Parsed Result:", result)

    # Return all details to frontend
    return jsonify({
    "name": result["name"],
    "email": result["email"],
    "phone": result["phone"],
    "skills": result["skills"],
    "education": result["education"],
    "experience": result["experience"],
    "certifications": result["certifications"]
})



# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
