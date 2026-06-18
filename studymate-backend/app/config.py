from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "StudyMate API"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "studymate_db"

    frontend_url: str = "http://localhost:5173"

    secret_key: str = "studymate_secret_key_dev_2026_change_when_deploy"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_from_name: str = "StudyMate"
    mail_server: str = "smtp.gmail.com"
    mail_port: int = 587
    mail_starttls: bool = True
    mail_ssl_tls: bool = False

    verification_token_expire_minutes: int = 30

    gemini_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings(
    
)