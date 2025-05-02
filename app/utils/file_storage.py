import os
import uuid
from fastapi import UploadFile
from pathlib import Path
from datetime import datetime
from app.config import settings

def save_upload_file(upload_file: UploadFile, subfolder: str = "") -> str:
    """Save an uploaded file and return the file path"""
    # Create a unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{timestamp}_{unique_id}_{upload_file.filename}"
    
    # Ensure the upload directory exists
    upload_dir = Path(settings.MEDIA_ROOT) / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the file
    file_path = upload_dir / filename
    with open(file_path, "wb") as f:
        content = upload_file.file.read()
        f.write(content)
        
    # Return relative path for storage in database
    return os.path.join(subfolder, filename)

def get_file_url(file_path: str) -> str:
    """Get the URL for a file"""
    if settings.STORAGE_TYPE == "local":
        return f"/media/{file_path}"
    # Add S3 or other storage handling here
    return file_path
