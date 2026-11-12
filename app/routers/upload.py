import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.utils.upload import (
    ALLOWED_EXTENSIONS,
    CHUNK_SIZE,
    MAX_FILE_SIZE,
    detect_image_type,
    upload_rate_limiter,
)

router = APIRouter(prefix="/upload", tags=["Upload"])
UPLOAD_DIR = Path("uploads")


@router.post(
    "/image",
    status_code=status.HTTP_201_CREATED,
    summary="Upload image file (Authenticated users only, max 5 MB)",
)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    # 1. Rate limiting check
    if not upload_rate_limiter.is_allowed(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Превышен лимит загрузок. Пожалуйста, подождите минуту.",
        )

    # 2. File extension validation
    filename_str = file.filename or ""
    client_ext = Path(filename_str).suffix.lower()
    if client_ext not in ALLOWED_EXTENSIONS:
        allowed_list = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимое расширение файла '{client_ext}'. Разрешены: {allowed_list}",
        )

    # 3. Read initial chunk for magic bytes signature detection
    first_chunk = await file.read(CHUNK_SIZE)
    canonical_ext = detect_image_type(first_chunk)
    if not canonical_ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл не является валидным изображением (JPEG, PNG, WebP или GIF).",
        )

    # 4. Stream and write to disk under secure UUID filename
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid.uuid4().hex}{canonical_ext}"
    target_path = UPLOAD_DIR / stored_filename

    total_bytes = len(first_chunk)
    if total_bytes > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE
            if hasattr(status, "HTTP_413_CONTENT_TOO_LARGE")
            else 413,
            detail="Размер файла превышает лимит 5 МБ.",
        )

    try:
        with open(target_path, "wb") as buffer:
            buffer.write(first_chunk)
            while chunk := await file.read(CHUNK_SIZE):
                total_bytes += len(chunk)
                if total_bytes > MAX_FILE_SIZE:
                    buffer.close()
                    if target_path.exists():
                        target_path.unlink()
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE
                        if hasattr(status, "HTTP_413_CONTENT_TOO_LARGE")
                        else 413,
                        detail="Размер файла превышает лимит 5 МБ.",
                    )
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as exc:
        if target_path.exists():
            target_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при сохранении файла на сервере.",
        ) from exc

    return {
        "url": f"/uploads/{stored_filename}",
        "filename": stored_filename,
        "size": total_bytes,
    }
