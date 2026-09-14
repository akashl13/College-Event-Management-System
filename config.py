import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-this-key")
    APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:5000")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///college_events.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    QR_CODE_DIR = os.path.join("app", "static", "qr_codes")
