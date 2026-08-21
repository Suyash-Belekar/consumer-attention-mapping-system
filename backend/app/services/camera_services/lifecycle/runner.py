"""
lifecycle/runner.py

The blocking start -> process_frame loop -> stop run loop, extracted
from CameraPipeline so pipeline.py stays focused on wiring, not loop
control flow.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.camera_services.pipeline import CameraPipeline

logger = logging.getLogger(__name__)


def run_pipeline(pipeline: "CameraPipeline") -> None:
    """Execute the complete camera pipeline: start, process, stop."""
    if not pipeline.start():
        return

    logger.info("Running camera pipeline...")
    try:
        while pipeline.running:
            if not pipeline.process_frame():
                break
            if pipeline.services.display_pipeline.should_exit():
                logger.info("Exit requested by user.")
                break
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received.")
    except Exception:
        logger.exception("Unhandled exception in camera pipeline.")
    finally:
        pipeline.stop()
