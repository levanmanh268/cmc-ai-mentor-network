"""FastAPI student-only demo using fictional lessons, never official FUNiX data."""
from fastapi import FastAPI
from pydantic import BaseModel, Field
from .core import EduService,Learner

app=FastAPI(title="EduTrainer AI Lab: Synthetic Education Capability",version="0.1.0")
service=EduService()
STUDENT=Learner("python-foundations","student")
class Query(BaseModel):
    question:str=Field(min_length=3,max_length=1500)
class Module(BaseModel):
    module:str=Field(min_length=1,max_length=80)
class Answers(BaseModel):
    answers:dict[str,str]
class Rubric(BaseModel):
    rubric_id:str=Field(min_length=3,max_length=50)
    submission:str=Field(min_length=1,max_length=4000)
class Progress(BaseModel):
    completed:list[str]=Field(default_factory=list,max_length=200)

@app.get("/health")
def health():
    return {"status":"ok","mode":"fictional_student_only","external_ai_calls":0,"official_lms_grades":False}

@app.post("/course/search")
def search(payload:Query):
    return service.search(STUDENT,payload.question)

@app.post("/quiz")
def quiz(payload:Module):
    return service.quiz(STUDENT,payload.module)

@app.post("/quiz/grade")
def grade(payload:Answers):
    return service.grade_quiz(STUDENT,payload.answers)

@app.post("/rubric/feedback")
def feedback(payload:Rubric):
    return service.rubric_feedback(STUDENT,payload.rubric_id,payload.submission)

@app.post("/learning/path")
def path(payload:Progress):
    return service.learning_path(STUDENT,payload.completed)
