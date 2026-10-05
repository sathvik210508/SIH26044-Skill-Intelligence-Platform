import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database.db import Base, engine
from app.seed.seed_data import seed_database
from app.api.auth_router import router as auth_router
from app.api.student_router import router as student_router
from app.api.assessment_router import router as assessment_router
from app.api.recruiter_router import router as recruiter_router
from app.api.institution_router import router as institution_router
from app.api.admin_router import router as admin_router
from app.api.ai_assistant_router import router as ai_assistant_router
from app.api.notifications_router import router as notifications_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB & Seed
    Base.metadata.create_all(bind=engine)
    try:
        seed_database()
    except Exception as e:
        print(f"Seed note: {e}")
    yield

app = FastAPI(
    title="SIH26044 — Real AI-Powered Skill Intelligence & Matching Platform",
    description="Full-stack prototype connecting Students, Recruiters, Institutions, and Ministry Authorities with a Central Skill Intelligence Engine.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router)
app.include_router(student_router)
app.include_router(assessment_router)
app.include_router(recruiter_router)
app.include_router(institution_router)
app.include_router(admin_router)
app.include_router(ai_assistant_router)
app.include_router(notifications_router)

# Frontend Static Files
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "SIH26044 Backend is running. Frontend index.html not yet created."}

@app.get("/health")
def health_check():
    return {"status": "healthy", "engine": "Skill Intelligence Engine v1.0", "ready": True}
