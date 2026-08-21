"""
pipeline.py

CameraPipeline: Thin orchestrator connecting camera feeds, service lifecycle,
performance monitoring, and per-frame analytics execution.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple

# System & Performance Utilities
from app.utils.performance import PerformanceMonitor

# Camera Service Infrastructure
from app.services.camera_services.config import CameraPipelineConfig
from app.services.camera_services.context import ContextManagerMixin
from app.services.camera_services.exceptions import CameraSourceError
from app.services.camera_services.source.camera_source import CameraSource
from app.services.camera_services.services.registry import build_services

# Lifecycle Helpers
from app.services.camera_services.lifecycle.startup import (
    print_banner,
    start_camera,
)
from app.services.camera_services.lifecycle.shutdown import (
    print_summary,
    release_resources,
)
from app.services.camera_services.lifecycle.runner import run_pipeline

# Processing Step
from app.services.camera_services.processing.frame_step import process_one_frame

logger = logging.getLogger(__name__)


class CameraPipeline(ContextManagerMixin):
    """
    Coordinates the webcam -> analytics -> display workflow.

    Usage:
        CameraPipeline(source=0).run()

    Context Manager:
        with CameraPipeline(source=0) as pipeline:
            pipeline.run()
    """

    def __init__(
        self,
        source: int | str = 0,
        config: Optional[CameraPipelineConfig] = None,
        *,
        store_id: object | None = None,
        camera_id: str | None = None,
        shelves_config: dict | None = None,
        zones_config: dict | None = None,
        products_config: dict | None = None,
        session_factory=None,
        display_config=None,
    ) -> None:
        self.source = source
        self.config = config or CameraPipelineConfig()

        self.camera = CameraSource(self.source, self.config)
        self.performance = PerformanceMonitor()
        self.store_id = store_id
        self.camera_id = camera_id
        self.session_factory = session_factory
        self.services = build_services(
            self.performance,
            store_id=store_id,
            camera_id=camera_id,
            shelves_config=shelves_config,
            zones_config=zones_config,
            products_config=products_config,
            session_factory=session_factory,
            display_config=display_config,
        )

        self.running: bool = False
        self._stopped: bool = False
        self.frame_number: int = 0
        self.stream_start: float = 0.0
        self.original_size: Optional[Tuple[int, int]] = None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"source={self.source!r}, "
            f"running={self.running}, "
            f"frames={self.frame_number})"
        )

    def start(self) -> bool:
        """Open the camera and initialize pipeline state.
        
        Returns:
            bool: True if startup succeeded, False otherwise.
        """
        logger.info("Starting Camera Pipeline for source=%r", self.source)
        try:
            self.stream_start = start_camera(self.camera)
        except CameraSourceError:
            logger.exception("Failed to start camera pipeline due to source error.")
            return False

        self.running = True
        self._stopped = False
        print_banner(self.config)
        return True

    def run(self) -> None:
        """Execute the complete camera pipeline lifecycle (start -> process loop -> stop)."""
        run_pipeline(self)

    def process_frame(self) -> bool:
        """Process a single camera frame.

        Returns:
            bool: False when the camera stream has ended or failed.
        """
        result = process_one_frame(
            camera=self.camera,
            services=self.services,
            current_frame_number=self.frame_number,
            stream_start=self.stream_start,
            known_original_size=self.original_size,
        )

        self.frame_number = result.frame_number
        if result.success:
            self.original_size = result.original_size

        return result.success

    def stop(self) -> None:
        """Stop the loop, release system resources, and log execution summary. Idempotent."""
        if self._stopped:
            return
        if not self.running and self.frame_number == 0:
            return

        logger.info("Stopping Camera Pipeline...")
        self.running = False

        release_resources(self.camera, self.services)
        print_summary(
            self.services,
            self.original_size,
            self.config.processed_size,
        )
        self._stopped = True
        logger.info("Camera pipeline stopped successfully.")