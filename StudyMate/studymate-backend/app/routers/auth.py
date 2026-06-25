import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.email_verification_token import EmailVerificationToken
from app.models.user import User
from app.schemas.auth_schema import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationRequest,
    UserResponse,
    VerifyEmailResponse,
)
from app.services.email_service import send_verification_email
from app.services.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

COOKIE_NAME = "studymate_session"


def build_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        role="Sinh viên",
    )


def create_verification_token(user_id: int) -> EmailVerificationToken:
    token_value = secrets.token_urlsafe(48)
    expires_at = datetime.now() + timedelta(
        minutes=settings.verification_token_expire_minutes
    )

    return EmailVerificationToken(
        user_id=user_id,
        token=token_value,
        expires_at=expires_at,
    )


def set_login_cookie(response: Response, user: User) -> None:
    token = create_access_token(user.id, user.email)

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


def get_current_user(
    studymate_session: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not studymate_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bạn chưa đăng nhập.",
        )

    payload = decode_access_token(studymate_session)

    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập không hợp lệ.",
        )

    user = db.get(User, int(payload["sub"]))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc chưa được kích hoạt.",
        )

    return user


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    normalized_email = data.email.lower().strip()

    existing_user = db.scalar(
        select(User).where(func.lower(User.email) == normalized_email)
    )

    if existing_user:
        if not existing_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Email này đã đăng ký nhưng chưa xác thực. "
                    "Vui lòng gửi lại email xác nhận."
                ),
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email này đã được sử dụng.",
        )

    user = User(
        full_name=data.full_name.strip(),
        email=normalized_email,
        password_hash=hash_password(data.password),
        avatar_url=None,
        is_active=False,
    )

    try:
        db.add(user)
        db.flush()

        verification_token = create_verification_token(user.id)
        db.add(verification_token)

        await send_verification_email(
            recipient_email=user.email,
            full_name=user.full_name,
            token=verification_token.token,
        )

        db.commit()

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể gửi email xác thực. "
                "Vui lòng kiểm tra cấu hình Gmail App Password."
            ),
        ) from error

    return RegisterResponse(
        message=(
            "Đăng ký thành công. "
            "Vui lòng kiểm tra email để xác thực tài khoản."
        ),
        email=user.email,
    )


@router.get(
    "/verify-email",
    response_model=VerifyEmailResponse,
)
def verify_email(
    token: str,
    db: Session = Depends(get_db),
):
    verification_token = db.scalar(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token == token
        )
    )

    if not verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Liên kết xác thực không hợp lệ.",
        )

    if verification_token.verified_at:
        return VerifyEmailResponse(
            message="Email này đã được xác thực trước đó.",
            verified=True,
        )

    if verification_token.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Liên kết xác thực đã hết hạn. Vui lòng gửi lại email.",
        )

    user = db.get(User, verification_token.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tài khoản không tồn tại.",
        )

    user.is_active = True
    verification_token.verified_at = datetime.now()

    db.commit()

    return VerifyEmailResponse(
        message="Xác thực email thành công. Bạn có thể đăng nhập.",
        verified=True,
    )


@router.post(
    "/resend-verification",
    response_model=RegisterResponse,
)
async def resend_verification_email(
    data: ResendVerificationRequest,
    db: Session = Depends(get_db),
):
    normalized_email = data.email.lower().strip()

    user = db.scalar(
        select(User).where(func.lower(User.email) == normalized_email)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tài khoản với email này.",
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản này đã được xác thực.",
        )

    try:
        db.execute(
            delete(EmailVerificationToken).where(
                EmailVerificationToken.user_id == user.id,
                EmailVerificationToken.verified_at.is_(None),
            )
        )

        verification_token = create_verification_token(user.id)
        db.add(verification_token)

        await send_verification_email(
            recipient_email=user.email,
            full_name=user.full_name,
            token=verification_token.token,
        )

        db.commit()

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể gửi lại email xác thực.",
        ) from error

    return RegisterResponse(
        message="Đã gửi lại email xác thực. Vui lòng kiểm tra hộp thư.",
        email=user.email,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
def login_user(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    normalized_email = data.email.lower().strip()

    user = db.scalar(
        select(User).where(func.lower(User.email) == normalized_email)
    )

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Tài khoản chưa được xác thực. "
                "Vui lòng kiểm tra email để kích hoạt tài khoản."
            ),
        )

    user.last_login_at = datetime.now()
    db.commit()
    db.refresh(user)

    set_login_cookie(response, user)

    return AuthResponse(
        message="Đăng nhập thành công.",
        user=build_user_response(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return build_user_response(current_user)


@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
    )

    return {
        "message": "Đăng xuất thành công.",
    }