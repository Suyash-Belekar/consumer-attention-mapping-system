# backend/app/api/camera.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import shutil

from app.core.database import get_db

router = APIRouter(prefix="/api/camera", tags=["Camera"])

@router.post(
    "/capture",
    status_code=status.HTTP_201_CREATED,
    description="Receive a JPEG image from the frontend and store it in the static heatmaps folder.",
)
async def capture_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),  # placeholder, not used currently
):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    # Save to static/heatmaps with a timestamped filename
    static_dir = Path(__file__).parents[3] / "static" / "heatmaps"
    static_dir.mkdir(parents=True, exist_ok=True)
    dest_path = static_dir / f"{int(Path(file.filename).stem)}_{int(Path(file.filename).suffix.lstrip('.'))}.jpg"
    try:
        with dest_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        await file.close()
    return {"filename": dest_path.name, "status": "saved"}
