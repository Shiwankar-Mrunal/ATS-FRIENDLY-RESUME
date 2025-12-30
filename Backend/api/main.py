from fastapi import FastAPI
from routes import resume, job
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ATS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*","http://127.0.0.1:5500"],  # Or your front-end URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include resume-related endpoints (parsing, scoring, ranking)
app.include_router(resume.router, prefix="/resume", tags=["Resume"])

# Include job-related endpoints (submit job description, get current job)
app.include_router(job.router, prefix="/job", tags=["Job"])

@app.get("/")
def root():
    """
    Health check endpoint
    """
    return {"message": "ATS Backend is running"}
