import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4"}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def infer_media_type(filename):
    extension = filename.rsplit(".", 1)[1].lower()
    if extension in ALLOWED_IMAGE_EXTENSIONS:
        return "image"
    if extension in ALLOWED_VIDEO_EXTENSIONS:
        return "video"
    return None


def save_media(file_storage):
    if not file_storage or file_storage.filename == "":
        return None, None

    if not allowed_file(file_storage.filename):
        raise ValueError("Only jpg, jpeg, png, and mp4 files are allowed.")

    filename = secure_filename(file_storage.filename)
    extension = filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{extension}"
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    destination = os.path.join(upload_dir, unique_name)
    file_storage.save(destination)
    return unique_name, infer_media_type(unique_name)
