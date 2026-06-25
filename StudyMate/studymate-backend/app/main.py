from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import SessionLocal, test_database_connection
from app.services.email_service import send_reminder_email

from app.routers.auth import router as auth_router
from app.routers.subjects import router as subjects_router
from app.routers.tasks import router as tasks_router
from app.routers.exams import router as exams_router
from app.routers.study_plans import router as study_plans_router
from app.routers.documents import router as documents_router
from app.routers.chatbot import router as chatbot_router


scheduler = AsyncIOScheduler()


async def process_pending_reminders():
    print("Checking reminders...")

    db = SessionLocal()

    try:
        reminders = db.execute(
            text("""
                SELECT *
                FROM reminders
                WHERE UPPER(status) = 'PENDING'
                  AND remind_at <= NOW()
            """)
        ).mappings().all()

        print(f"Found {len(reminders)} reminders")

        for reminder in reminders:
            try:
                await send_reminder_email(
                    recipient_email=reminder["email_to"],
                    title=f"Nhắc nhở {reminder['target_type']}",
                    deadline=str(reminder["remind_at"])
                )

                db.execute(
                    text("""
                        UPDATE reminders
                        SET status = 'SENT',
                            sent_at = NOW()
                        WHERE id = :id
                    """),
                    {"id": reminder["id"]}
                )

                print(
                    f"Sent reminder #{reminder['id']} "
                    f"to {reminder['email_to']}"
                )

            except Exception as error:
                print(f"Email error: {error}")

        db.commit()

    except Exception as error:
        print(f"Scheduler error: {error}")

    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        process_pending_reminders,
        "interval",
        seconds=10
    )

    scheduler.start()

    print("Reminder scheduler started")

    yield

    scheduler.shutdown()


app = FastAPI(
    title=settings.app_name,
    description="Backend cho hệ thống trợ lý học tập cá nhân StudyMate",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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