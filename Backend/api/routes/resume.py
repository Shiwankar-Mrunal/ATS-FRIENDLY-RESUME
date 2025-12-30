# from fastapi import APIRouter

# router = APIRouter()

# # Temporary in-memory ranking
# CANDIDATES = []

# @router.post("/add")
# def add_candidate(name: str, score: float):
#     CANDIDATES.append({"name": name, "score": score})
#     return {"message": "Candidate added"}

# @router.get("/")
# def get_ranking():
#     ranked = sorted(CANDIDATES, key=lambda x: x["score"], reverse=True)
#     return ranked


# _______________________________________________________________________________________
# from fastapi import APIRouter

# router = APIRouter()

# CANDIDATES = []

# def calculate_score(resume_skills, job_skills):
#     if not job_skills:
#         return 0

#     matched = set(resume_skills) & set(job_skills)
#     return round((len(matched) / len(job_skills)) * 100, 2)

# @router.post("/add")
# def add_candidate(name: str, resume_skills: list, job_skills: list):
#     score = calculate_score(resume_skills, job_skills)

#     CANDIDATES.append({
#         "name": name,
#         "score": score,
#         "matched_skills": list(set(resume_skills) & set(job_skills))
#     })

#     return {"message": "Candidate scored", "score": score}

# @router.get("/")
# def get_ranking():
#     return sorted(CANDIDATES, key=lambda x: x["score"], reverse=True)
#_________________________________________________________________________________________________

# 


from fastapi import APIRouter, UploadFile, File
from resume_parser import parse_resume
import io
from typing import List
from PyPDF2 import PdfReader  # for PDF files

router = APIRouter()

CANDIDATES = []

def calculate_score(resume_skills, job_skills):
    if not job_skills:
        return 0
    matched = set(resume_skills) & set(job_skills)
    return round((len(matched) / len(job_skills)) * 100, 2)

@router.post("/add")
def add_candidate(name: str, resume_skills: List[str], job_skills: List[str]):
    score = calculate_score(resume_skills, job_skills)
    CANDIDATES.append({
        "name": name,
        "score": score,
        "matched_skills": list(set(resume_skills) & set(job_skills))
    })
    return {"message": "Candidate scored", "score": score}

@router.get("/")
def get_ranking():
    return sorted(CANDIDATES, key=lambda x: x["score"], reverse=True)

# ----------------------------
# Resume parsing endpoint for file upload
# ----------------------------
@router.post("/parse-file")
async def parse_resume_file(file: UploadFile = File(...)):
    """
    Accept a resume file (PDF or TXT) and extract details.
    """

    content = await file.read()
    
    text = ""
    if file.content_type == "application/pdf":
        pdf_reader = PdfReader(io.BytesIO(content))
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    elif file.content_type in ["text/plain"]:
        text = content.decode("utf-8", errors="ignore")
    else:
        return {"error": "Unsupported file type. Only PDF or TXT allowed."}

    parsed_data = parse_resume(text)
    return parsed_data

