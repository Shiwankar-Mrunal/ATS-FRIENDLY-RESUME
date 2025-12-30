from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

SKILLS_DB = [
    "Python", "Java", "JavaScript", "React",
    "SQL", "FastAPI", "Django", "Machine Learning"
]

CURRENT_JOB = {}

class JobDescription(BaseModel):
    text: str

def extract_skills(text: str):
    return [skill for skill in SKILLS_DB if skill.lower() in text.lower()]

@router.post("/submit")
def submit_job(job: JobDescription):
    """
    Save the current job description and extract required skills.
    """
    skills = extract_skills(job.text)
    CURRENT_JOB["skills"] = skills

    return {
        "message": "Job saved",
        "required_skills": skills,
        "total_skills": len(skills)
    }

@router.get("/current")
def get_current_job():
    """
    Get the current job description skills.
    """
    return CURRENT_JOB
