from __future__ import annotations

from pathlib import Path
from uuid import UUID

import cv2
import numpy as np

HEATMAP_DIR = Path("static/heatmaps")
HEATMAP_DIR.mkdir(parents=True, exist_ok=True)


def _base_image(path: str | None, width: int, height: int):
    if path:
        image = cv2.imread(path)
        if image is not None:
            return cv2.resize(image, (width, height))
    return np.zeros((height, width, 3), dtype=np.uint8)


def generate_heatmap_overlay(
    store_id: UUID | str,
    tracking_points: list[dict],
    *,
    base_image_path: str | None = None,
    width: int = 1280,
    height: int = 720,
    heatmap_type: str = "traffic",
) -> str:
    """Generate a deterministic OpenCV heatmap from persisted tracking points."""
    canvas = _base_image(base_image_path, width, height)
    density = np.zeros((height, width), dtype=np.float32)

    for point in tracking_points:
        x = int(float(point.get("x", 0)))
        y = int(float(point.get("y", 0)))
        if 0 <= x < width and 0 <= y < height:
            value = float(point.get("value", 1.0) or 1.0)
            density[y, x] += max(value, 0.0)

    if density.max() <= 0:
        overlay = canvas
    else:
        density = cv2.GaussianBlur(density, (0, 0), sigmaX=25, sigmaY=25)
        normalized = cv2.normalize(density, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        color_map = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
        mask = (normalized.astype(np.float32) / 255.0)[..., None]
        overlay = (canvas.astype(np.float32) * 0.65 + color_map.astype(np.float32) * (0.15 + 0.55 * mask)).clip(0, 255).astype(np.uint8)

    HEATMAP_DIR.mkdir(parents=True, exist_ok=True)
    safe_store = str(store_id).replace("-", "")
    output = HEATMAP_DIR / f"store_{safe_store}_{heatmap_type}.jpg"
    if not cv2.imwrite(str(output), overlay):
        raise RuntimeError("Failed to write generated heatmap image.")
    return str(output)
