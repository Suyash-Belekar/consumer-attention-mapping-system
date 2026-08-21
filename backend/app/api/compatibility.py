"""Backward-compatible endpoints retained for the previous frontend build."""
from pathlib import Path
import shutil
from fastapi import APIRouter, File, UploadFile, HTTPException

router = APIRouter(prefix="/api/camera", tags=["Camera Compatibility"])

@router.post("/capture", status_code=201)
async def capture_image(file: UploadFile = File(...)):
    if file.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(400, "Unsupported image type.")
    directory = Path("static/uploads/captures")
    directory.mkdir(parents=True, exist_ok=True)
    filename = Path(file.filename or "capture.jpg").name
    target = directory / filename
    with target.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    await file.close()
    return {"filename": target.name, "url": f"/static/uploads/captures/{target.name}", "status": "saved"}
