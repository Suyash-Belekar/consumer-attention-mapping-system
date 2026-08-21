"""
context.py

Context-manager support for CameraPipeline (`with CameraPipeline(...)
as p:`), split into its own mixin so pipeline.py stays focused on
orchestration logic rather than dunder-method plumbing.
"""

from __future__ import annotations

from app.services.camera_services.exceptions import CameraSourceError


class ContextManagerMixin:
    """Adds `with CameraPipeline(...) as p:` support via start()/stop().

    Requires the composing class to define `self.source`, `start()`,
    and `stop()`.
    """

    def __enter__(self):
        if not self.start():
            raise CameraSourceError(f"Failed to start source={self.source!r}")
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.stop()
