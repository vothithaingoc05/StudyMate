from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import test_database_connection

from app.routers.auth import router as auth_router
from app.routers.subjects import router as subjects_router
from app.routers.tasks import router as tasks_router

from app.routers.exams import router as exams_router
from app.routers.study_plans import router as study_plans_router
from app.routers.documents import router as documents_router
from app.routers.chatbot import router as chatbot_router


app = FastAPI(
    title=settings.app_name,
    description="Backend cho hệ thống trợ lý học tập cá nhân StudyMate",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(subjects_router)
app.include_router(tasks_router)

app.include_router(exams_router)
app.include_router(study_plans_router)
app.include_router(documents_router)
app.include_router(chatbot_router)


@app.get("/")
def home():
    return {
        "message": "StudyMate Backend đang hoạt động",
        "api_docs": "/docs",
    }


@app.get("/api/health")
def health_check():
    database_result = test_database_connection()

    if database_result["connected"]:
        return {
            "status": "success",
            "message": "Kết nối MariaDB XAMPP thành công",
            "database": database_result["database"],
            "number_of_tables": database_result["table_count"],
            "tables": database_result["tables"],
        }

    return {
        "status": "error",
        "message": "Không thể kết nối database",
        "detail": database_result["error"],
    }