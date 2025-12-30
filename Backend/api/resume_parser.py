# from pydantic import BaseModel
# from typing import List

# class ResumeUpload(BaseModel):
#     name: str
#     job_description: str
#     resume_text: str

# class CandidateScore(BaseModel):
#     name: str
#     score: float

# class RankingResponse(BaseModel):
#     candidates: List[CandidateScore]


import re
import spacy

nlp = spacy.load("en_core_web_sm")

SKILLS_DB = [
    "Python", "Java", "JavaScript", "React",
    "SQL", "FastAPI", "Django",
    "Machine Learning", "AWS", "Docker"
]

def extract_email(text: str):
    match = re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", text)
    return match.group(0) if match else None


def extract_phone(text: str):
    match = re.search(r"\+?\d[\d\s\-]{8,15}", text)
    return match.group(0) if match else None

def extract_name(text: str):
    lines = text.splitlines()
    first_lines = " ".join(lines[:3])  # usually name is here

    doc = nlp(first_lines)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()
    return None


SECTION_HEADERS = {
    "skills": ["skills", "technical skills"],
    "experience": ["experience", "work experience", "employment"],
    "education": ["education", "academic"]
}

def extract_sections(text: str):
    sections = {}
    lines = text.splitlines()

    current_section = None
    buffer = []

    for line in lines:
        line_clean = line.lower().strip()

        matched_section = None
        for section, keywords in SECTION_HEADERS.items():
            if line_clean in keywords:
                matched_section = section
                break

        if matched_section:
            if current_section:
                sections[current_section] = "\n".join(buffer)
            current_section = matched_section
            buffer = []
        elif current_section:
            buffer.append(line)

    if current_section:
        sections[current_section] = "\n".join(buffer)

    return sections


def extract_skills(text: str):
    text_lower = text.lower()
    skills = set()

    for skill in SKILLS_DB:
        if skill.lower() in text_lower:
            skills.add(skill)  # keep canonical form

    return sorted(list(skills))


def clean_lines(section_text: str):
    lines = []
    for line in section_text.split("\n"):
        line = line.strip("•- \t")
        if len(line) > 3:
            lines.append(line)
    return lines


def extract_experience(section_text: str):
    return clean_lines(section_text) if section_text else []


def extract_education(section_text: str):
    return clean_lines(section_text) if section_text else []



def parse_resume(text: str):
    sections = extract_sections(text)

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(sections.get("skills", text)),
        "experience": extract_experience(sections.get("experience")),
        "education": extract_education(sections.get("education"))
    }

