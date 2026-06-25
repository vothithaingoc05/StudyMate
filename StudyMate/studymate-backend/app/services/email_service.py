from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.config import settings


def get_mail_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_FROM=settings.mail_from or "noreply@studymate.com",
        MAIL_FROM_NAME=settings.mail_from_name,
        MAIL_PORT=settings.mail_port,
        MAIL_SERVER=settings.mail_server,
        MAIL_STARTTLS=settings.mail_starttls,
        MAIL_SSL_TLS=settings.mail_ssl_tls,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )


async def send_verification_email(
    recipient_email: str,
    full_name: str,
    token: str,
) -> None:
    verification_link = (
        f"{settings.frontend_url}/xac-thuc-email?token={token}"
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
      <body style="margin:0; padding:0; background:#f5f7fb; font-family:Arial, sans-serif;">
        <div style="max-width:560px; margin:34px auto; padding:36px; border-radius:18px;
                    background:#ffffff; border:1px solid #eef0f5;">
          <div style="margin-bottom:23px; color:#4f46e5; font-size:26px; font-weight:700;">
            StudyMate
          </div>

          <h2 style="margin:0 0 16px; color:#111827;">
            Xác nhận địa chỉ email
          </h2>

          <p style="color:#4b5563; line-height:1.7;">
            Xin chào <strong>{full_name}</strong>,
          </p>

          <p style="color:#4b5563; line-height:1.7;">
            Bạn vừa đăng ký tài khoản StudyMate. Hãy nhấn nút bên dưới để
            xác thực email và kích hoạt tài khoản của bạn.
          </p>

          <div style="margin:30px 0;">
            <a href="{verification_link}"
               style="display:inline-block; padding:14px 25px; border-radius:11px;
                      color:#ffffff; background:#6366f1; text-decoration:none;
                      font-weight:700;">
              Xác thực email
            </a>
          </div>

          <p style="color:#6b7280; font-size:13px; line-height:1.65;">
            Liên kết xác thực có hiệu lực trong
            {settings.verification_token_expire_minutes} phút.
            Nếu bạn không đăng ký tài khoản StudyMate, hãy bỏ qua email này.
          </p>
        </div>
      </body>
    </html>
    """

    message = MessageSchema(
        subject="Xác thực tài khoản StudyMate",
        recipients=[recipient_email],
        body=html_content,
        subtype=MessageType.html,
    )

    fast_mail = FastMail(get_mail_config())
    await fast_mail.send_message(message)


async def send_reminder_email(
    recipient_email: str,
    title: str,
    deadline: str,
) -> None:
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
      <body style="font-family: Arial, sans-serif;">
        <h2>Nhắc nhở từ StudyMate</h2>

        <p>
          <strong>{title}</strong>
        </p>

        <p>
          Thời gian nhắc:
          <strong>{deadline}</strong>
        </p>

        <p>
          Vui lòng đăng nhập StudyMate để xem chi tiết.
        </p>
      </body>
    </html>
    """

    message = MessageSchema(
        subject="Nhắc nhở học tập - StudyMate",
        recipients=[recipient_email],
        body=html_content,
        subtype=MessageType.html,
    )

    fast_mail = FastMail(get_mail_config())
    await fast_mail.send_message(message)