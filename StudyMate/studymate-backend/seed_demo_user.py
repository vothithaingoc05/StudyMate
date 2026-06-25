from sqlalchemy import func, select

from app.database import SessionLocal
from app.models.user import User
from app.services.security import hash_password


DEMO_FULL_NAME = "Võ Thị Thái Ngọc"
DEMO_EMAIL = "vothithaingoc072005@gmail.com"
DEMO_PASSWORD = "123456"


def seed_demo_user() -> None:
    db = SessionLocal()

    try:
        user = db.get(User, 1)

        if not user:
            user = db.scalar(
                select(User).where(
                    func.lower(User.email) == DEMO_EMAIL.lower()
                )
            )

        if user:
            user.full_name = DEMO_FULL_NAME
            user.email = DEMO_EMAIL
            user.password_hash = hash_password(DEMO_PASSWORD)
            user.avatar_url = None
            user.is_active = True
        else:
            user = User(
                full_name=DEMO_FULL_NAME,
                email=DEMO_EMAIL,
                password_hash=hash_password(DEMO_PASSWORD),
                avatar_url=None,
                is_active=True,
            )
            db.add(user)

        db.commit()
        db.refresh(user)

        print("========================================")
        print("TAI KHOAN DEMO DA SAN SANG")
        print("========================================")
        print(f"ID       : {user.id}")
        print(f"Ho ten   : {user.full_name}")
        print(f"Email    : {user.email}")
        print(f"Mat khau : {DEMO_PASSWORD}")
        print("========================================")

    except Exception as error:
        db.rollback()
        print("LOI: Khong the tao hoac cap nhat tai khoan demo.")
        print(error)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_user()