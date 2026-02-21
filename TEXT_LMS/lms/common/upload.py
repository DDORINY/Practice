import os, uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}

def save_profile_image(file_storage) -> str | None:
    if not file_storage or file_storage.filename == "":
        return None

    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXT:
        raise ValueError("invalid image type")

    new_name = f"{uuid.uuid4().hex}.{ext}"
    save_dir = current_app.config["UPLOAD_PROFILE_DIR"]
    os.makedirs(save_dir, exist_ok=True)

    file_storage.save(os.path.join(save_dir, new_name))
    return new_name
