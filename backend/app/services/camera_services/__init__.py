"""
camera/__init__.py

Public API of the camera pipeline package. External code should import
from here (`app.services.pipeline.camera`) rather than reaching into
the subpackages directly.
"""

from .pipeline import CameraPipeline
from .config import CameraPipelineConfig
from .exceptions import (
    CameraPipelineError,
    CameraSourceError,
)

__all__ = [
    "CameraPipeline",
    "CameraPipelineConfig",
    "CameraPipelineError",
    "CameraSourceError",
]