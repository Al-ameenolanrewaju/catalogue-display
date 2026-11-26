import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app

try:
    import cloudinary
    import cloudinary.uploader
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False


def is_allowed_file(filename: str) -> bool:
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'webp', 'svg'})


def save_image_file(file_storage, folder: str = 'projects') -> str:
    """
    Saves an uploaded file either to Cloudinary (if configured)
    or to local static storage.
    Returns the public URL (or relative URL).
    """
    if not file_storage or not file_storage.filename:
        return None

    if not is_allowed_file(file_storage.filename):
        raise ValueError("Unsupported image format. Allowed: PNG, JPG, JPEG, WEBP, SVG.")

    # Check Cloudinary configuration
    cloud_name = current_app.config.get('CLOUDINARY_CLOUD_NAME')
    api_key = current_app.config.get('CLOUDINARY_API_KEY')
    api_secret = current_app.config.get('CLOUDINARY_API_SECRET')

    if CLOUDINARY_AVAILABLE and cloud_name and api_key and api_secret:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        res = cloudinary.uploader.upload(
            file_storage,
            folder=f"catalogue/{folder}",
            resource_type="image"
        )
        return res.get('secure_url')

    # Fallback to local static storage
    upload_dir = Path(current_app.config['UPLOAD_FOLDER']) / folder
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'jpg'
    unique_name = f"{uuid.uuid4().hex}.{extension}"
    destination = upload_dir / unique_name

    file_storage.save(str(destination))
    return f"/static/uploads/{folder}/{unique_name}"
