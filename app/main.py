from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, observations, approvals, teacher_assignments, monthly_report_router, acr, users, lists, academic_year, class_yearly_strength, salary, question_router
from app.scripts.seed import seed as seed_data

app = FastAPI(title="Teacher Review System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(observations.router)
app.include_router(approvals.router)
app.include_router(teacher_assignments.router)
app.include_router(monthly_report_router.router)
app.include_router(academic_year.router)
app.include_router(acr.router)
app.include_router(users.router)
app.include_router(lists.router)
app.include_router(class_yearly_strength.router)
app.include_router(salary.router)
app.include_router(question_router.router)

@app.get("/")
def root():
    return {"message": "Teacher Review System API is running"}

@app.on_event("startup")
def startup_event():
    seed_data()