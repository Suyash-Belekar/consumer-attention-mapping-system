"""
camera.py

Consumer Attention Mapping System

Application Entry Point

Responsibilities
----------------
• Create the Camera Pipeline
• Launch the application
• Handle top-level exceptions

This module intentionally contains no computer vision,
analytics, rendering, or storage logic.
"""

from __future__ import annotations

import logging

from app.services.camera_services.pipeline import CameraPipeline

logger = logging.getLogger(__name__)


def run_camera(source: int | str = 0) -> None:
    """
    Start the Consumer Attention Mapping camera pipeline.

    Parameters
    ----------
    source:
        Camera index or video file path.
    """

    logger.info("Starting Camera Pipeline...")

    pipeline = CameraPipeline(source)

    try:
        pipeline.run()

    except KeyboardInterrupt:
        logger.info("Camera pipeline interrupted by user.")

    except Exception:
        logger.exception("Unexpected error while running the camera pipeline.")

    finally:
        logger.info("Camera Pipeline stopped.")


def main() -> None:
    """
    Default application entry point.

    Launches the webcam (camera index 0).
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    run_camera(0)


if __name__ == "__main__":
    main()