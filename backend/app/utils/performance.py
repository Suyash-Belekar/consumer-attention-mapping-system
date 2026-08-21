"""
performance.py

PerformanceMonitor: tracks per-frame timing, rolling FPS, and peak
memory usage for the camera pipeline, and prints console diagnostics.

This module does NOT:
    * Touch the camera, detector, tracker, or any pipeline directly
    * Decide when to print — callers control that via the methods below
"""

from __future__ import annotations

import logging
import time
from collections import deque
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False
    logger.warning(
        "psutil not installed — memory tracking will report 0.0 MB. "
        "Install with: pip install psutil"
    )


class PerformanceMonitor:
    """Tracks timing, FPS, and memory for the running camera pipeline.

    Usage:
        timer = performance.start_timer()
        ... do frame work ...
        processing_time = performance.stop_timer(timer)
        fps = performance.current_fps()
        performance.update_memory()
        performance.print_frame_statistics(...)
        ...
        performance.summary(original_resolution=..., processed_resolution=...)
    """

    def __init__(self, fps_window: int = 30) -> None:
        self._frame_times: deque[float] = deque(maxlen=fps_window)
        self._peak_memory_mb: float = 0.0
        self._frames_processed: int = 0
        self._run_start = time.perf_counter()
        self._process = psutil.Process() if _HAS_PSUTIL else None

    # ------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------

    def start_timer(self) -> float:
        """Start timing a frame. Returns an opaque handle for stop_timer()."""
        return time.perf_counter()

    def stop_timer(self, timer: float) -> float:
        """Stop timing a frame started with start_timer(). Returns elapsed seconds."""
        elapsed = time.perf_counter() - timer
        self._frame_times.append(elapsed)
        self._frames_processed += 1
        return elapsed

    def current_fps(self) -> float:
        """Rolling average FPS over the last `fps_window` frames."""
        if not self._frame_times:
            return 0.0
        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0

    # ------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------

    def update_memory(self) -> float:
        """Sample current process memory (RSS, MB) and track the peak.

        Returns 0.0 if psutil is not installed rather than raising, so
        the capture loop never breaks over a missing optional dependency.
        """
        if self._process is None:
            return 0.0

        current_mb = self._process.memory_info().rss / (1024 * 1024)
        self._peak_memory_mb = max(self._peak_memory_mb, current_mb)
        return current_mb

    # ------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------

    def print_frame_statistics(
        self,
        frame_number: int,
        metadata: object,
        detections: int,
        tracked: int,
        processing_time: float,
    ) -> None:
        """Print a single-line per-frame diagnostic to the console."""
        # Base line
        line = (
            f"[Frame {frame_number:>6}] "
            f"detections={detections:<3} "
            f"tracked={tracked:<3} "
            f"time={processing_time * 1000:6.1f}ms "
            f"fps={self.current_fps():5.1f}"
        )

        # Append per-stage timings if provided in metadata
        try:
            stage_times = getattr(metadata, 'get', None) and metadata.get('stage_times') or None
            if stage_times:
                det_ms = stage_times.get('detector', 0.0) * 1000.0
                trk_ms = stage_times.get('tracker', 0.0) * 1000.0
                line += f" | detector={det_ms:5.1f}ms tracker={trk_ms:5.1f}ms"
        except Exception:
            # Never fail logging on timing display
            pass

        print(line)

    def summary(
        self,
        original_resolution: Optional[tuple[int, int]],
        processed_resolution: tuple[int, int],
    ) -> None:
        """Print a final run summary. Safe to call even if 0 frames ran."""
        total_runtime = time.perf_counter() - self._run_start
        avg_fps = (
            self._frames_processed / total_runtime if total_runtime > 0 else 0.0
        )

        print("\n" + "=" * 60)
        print("Performance Summary")
        print("=" * 60)
        print(f"Frames processed:     {self._frames_processed}")
        print(f"Total runtime:        {total_runtime:.1f}s")
        print(f"Average FPS:          {avg_fps:.1f}")
        print(f"Original resolution:  {original_resolution or 'N/A'}")
        print(f"Processed resolution: {processed_resolution}")

        if _HAS_PSUTIL:
            print(f"Peak memory usage:    {self._peak_memory_mb:.1f} MB")
        else:
            print("Peak memory usage:    N/A (psutil not installed)")

        print("=" * 60)