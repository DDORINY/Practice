import os

class Config:
    SECRET_KEY = "text_lms_secret"
    DB_HOST = "localhost"
    DB_USER = "mbc_text"
    DB_PASSWORD = "1234"
    DB_NAME = "lms_text"

    UPLOAD_PROFILE_DIR = os.path.join("static", "uploads", "profile")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
