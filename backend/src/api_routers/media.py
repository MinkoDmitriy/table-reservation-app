import os
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from src.core.storage import BaseStorage, get_storage

router = APIRouter(prefix="/media", tags=["Media"])

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    storage: BaseStorage = Depends(get_storage)
):
    # Get file extension and validate
    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()
    
    if ext not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат файла. Разрешены только PNG, JPG, JPEG и WEBP."
        )
    
    # Upload via chosen strategy (Local or S3)
    path = await storage.upload_file(file)
    return {"image_path": path}
