from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List

from ..services.database import get_db
from ..services.auth import get_current_user
from ..services.media import save_upload_file, save_multiple_files
from ..services.crud import create_media_file
from ..models.model import User
from ..schemas.schema import MediaUploadResponse

router = APIRouter(
    prefix="/api/media",
    tags=["media"],
    responses={404: {"description": "Not found"}}
)

@router.post("/upload", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a single media file.
    """
    try:
        # Save file to storage
        file_info = await save_upload_file(file, current_user.id)
        
        # Save file record to database
        db_media = create_media_file(
            db,
            user_id=current_user.id,
            filename=file_info["filename"],
            file_path=file_info["file_path"],
            file_url=file_info["file_url"],
            mime_type=file_info["mime_type"],
            file_size=file_info["file_size"]
        )
        
        return MediaUploadResponse(
            id=db_media.id,
            filename=db_media.filename,
            file_url=db_media.file_url
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.post("/upload-multiple", response_model=List[MediaUploadResponse])
async def upload_multiple_media(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload multiple media files (up to 9).
    """
    try:
        # Save files to storage
        file_infos = await save_multiple_files(files, current_user.id)
        
        # Save file records to database
        result = []
        for file_info in file_infos:
            db_media = create_media_file(
                db,
                user_id=current_user.id,
                filename=file_info["filename"],
                file_path=file_info["file_path"],
                file_url=file_info["file_url"],
                mime_type=file_info["mime_type"],
                file_size=file_info["file_size"]
            )
            
            result.append(MediaUploadResponse(
                id=db_media.id,
                filename=db_media.filename,
                file_url=db_media.file_url
            ))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload files: {str(e)}"
        ) 