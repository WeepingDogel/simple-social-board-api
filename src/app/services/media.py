import os
import shutil
import uuid
from fastapi import UploadFile, HTTPException
from typing import List
import mimetypes
from PIL import Image
import io

# Base directory for file storage
MEDIA_DIR = os.environ.get("MEDIA_DIR", "static/media")
# Maximum file size in bytes (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024
# Allowed image mime types
ALLOWED_MIME_TYPES = [
    "image/jpeg", 
    "image/png", 
    "image/gif", 
    "image/webp"
]

def ensure_media_dir():
    """Ensure media directory exists"""
    if not os.path.exists(MEDIA_DIR):
        os.makedirs(MEDIA_DIR, exist_ok=True)
    
    # Create user uploads directory
    user_uploads_dir = os.path.join(MEDIA_DIR, "uploads")
    if not os.path.exists(user_uploads_dir):
        os.makedirs(user_uploads_dir, exist_ok=True)
    
    return user_uploads_dir

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower() if filename else ""

def validate_image_file(file: UploadFile) -> bool:
    """Validate image file size and type"""
    # Check file size by reading content (may be slow for large files)
    file.file.seek(0, 2)  # Go to end of file
    file_size = file.file.tell()  # Get file size
    file.file.seek(0)  # Reset file position
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes")
    
    # Check file content type
    content_type = file.content_type
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"File type {content_type} not allowed. Allowed types: {ALLOWED_MIME_TYPES}")
    
    # Additional validation: try opening as image
    try:
        image_data = file.file.read()
        file.file.seek(0)  # Reset file position after reading
        
        img = Image.open(io.BytesIO(image_data))
        img.verify()  # Verify image integrity
        
        # Re-open to check dimensions/metadata
        img = Image.open(io.BytesIO(image_data))
        
        # Additional image validation could be done here
        # e.g. check dimensions, aspect ratio, etc.
        
        return True
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename to avoid collisions"""
    extension = get_file_extension(original_filename)
    return f"{uuid.uuid4().hex}{extension}"

async def save_upload_file(file: UploadFile, user_id: int) -> dict:
    """
    Save an uploaded file to the media directory
    Returns file info for database storage
    """
    # Ensure media directory exists
    user_uploads_dir = ensure_media_dir()
    
    # Validate file
    validate_image_file(file)
    
    # Create user directory if it doesn't exist
    user_dir = os.path.join(user_uploads_dir, str(user_id))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True)
    
    # Generate unique filename
    filename = generate_unique_filename(file.filename)
    
    # File path
    file_path = os.path.join(user_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Generate URL
    relative_path = os.path.join("media", "uploads", str(user_id), filename)
    file_url = f"/static/{relative_path}"
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Return file info for database
    return {
        "filename": file.filename,
        "saved_filename": filename,
        "file_path": file_path,
        "file_url": file_url,
        "mime_type": file.content_type,
        "file_size": file_size
    }

async def save_multiple_files(files: List[UploadFile], user_id: int) -> List[dict]:
    """Save multiple uploaded files and return their info"""
    if len(files) > 9:
        raise HTTPException(status_code=400, detail="Maximum 9 images allowed per post")
    
    results = []
    for file in files:
        file_info = await save_upload_file(file, user_id)
        results.append(file_info)
    
    return results 