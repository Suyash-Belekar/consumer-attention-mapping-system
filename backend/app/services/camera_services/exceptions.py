"""
exceptions.py

Custom exceptions for the camera pipeline package.
"""


class CameraPipelineError(Exception):
    """Base exception for all CameraPipeline failures."""


class CameraSourceError(CameraPipelineError):
    """Raised when a video source cannot be opened or never yields a frame."""
