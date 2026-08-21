from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# ==========================================================
# Type Aliases
# ==========================================================

BoundingBox = tuple[int, int, int, int]
Point2D = tuple[float, float]
Point3D = tuple[float, float, float]


# ==========================================================
# Landmark
# ==========================================================


@dataclass(slots=True, frozen=True)
class Landmark3D:
    """
    One facial landmark produced by MediaPipe Face Mesh.
    """

    x: float
    y: float
    z: float

    @property
    def point(self) -> Point3D:
        return (
            self.x,
            self.y,
            self.z,
        )


# ==========================================================
# Face Crop
# ==========================================================


@dataclass(slots=True)
class FaceCrop:
    """
    Cropped shopper face extracted from
    the tracked person's bounding box.
    """

    track_id: int

    image: object

    bbox: BoundingBox

    confidence: float

    timestamp: float

    @property
    def center(self) -> Point2D:

        x1, y1, x2, y2 = self.bbox

        return (
            (x1 + x2) / 2,
            (y1 + y2) / 2,
        )


# ==========================================================
# Face Mesh
# ==========================================================


@dataclass(slots=True)
class FaceMeshResult:
    """
    Facial landmarks extracted from MediaPipe Face Mesh.
    """

    track_id: int

    image: object

    bbox: BoundingBox

    landmarks: list[Landmark3D]

    confidence: float

    timestamp: float

    @property
    def landmark_count(self) -> int:
        return len(self.landmarks)


# ==========================================================
# Head Pose
# ==========================================================


@dataclass(slots=True)
class HeadPose:
    """
    Estimated head orientation.
    """

    track_id: int

    yaw: float

    pitch: float

    roll: float

    confidence: float

    timestamp: float


# ==========================================================
# Gaze Projection
# ==========================================================


@dataclass(slots=True)
class GazeProjection:
    """
    2D gaze ray projected into image coordinates.
    """

    track_id: int

    origin_x: float

    origin_y: float

    direction_x: float

    direction_y: float

    timestamp: float

    @property
    def origin(self) -> Point2D:
        return (
            self.origin_x,
            self.origin_y,
        )

    @property
    def direction(self) -> Point2D:
        return (
            self.direction_x,
            self.direction_y,
        )


# ==========================================================
# Attention Session
# ==========================================================


@dataclass(slots=True)
class AttentionRecord:
    """
    Represents one shopper attention session.
    """

    track_id: int

    shelf_id: Optional[int]

    entry_time: float

    last_seen: float

    exit_time: Optional[float] = None

    attention_time: float = 0.0

    confidence: float = 0.0

    active: bool = True

    @property
    def duration(self) -> float:
        return self.attention_time

    @property
    def person_id(self) -> int:
        """
        Backward compatibility.
        """
        return self.track_id


# ==========================================================
# Runtime Snapshot
# ==========================================================


@dataclass(slots=True)
class AttentionSnapshot:
    """
    Lightweight runtime snapshot.
    """

    active_sessions: int = 0

    completed_sessions: int = 0

    average_attention_time: float = 0.0

    maximum_attention_time: float = 0.0

    minimum_attention_time: float = 0.0

    total_attention_time: float = 0.0


# ==========================================================
# Statistics
# ==========================================================


@dataclass(slots=True)
class AttentionStatistics:
    """
    Aggregated statistics used by dashboards.
    """

    total_sessions: int = 0

    active_sessions: int = 0

    completed_sessions: int = 0

    average_attention_time: float = 0.0

    maximum_attention_time: float = 0.0

    minimum_attention_time: float = 0.0

    total_attention_time: float = 0.0

    most_viewed_shelf: Optional[int] = None


# ==========================================================
# Runtime State
# ==========================================================


@dataclass(slots=True)
class AttentionState:
    """
    Lightweight runtime state exposed by the
    attention subsystem.
    """

    active_count: int = 0

    completed_count: int = 0

    timestamp: float = 0.0

    snapshot: AttentionSnapshot = field(
        default_factory=AttentionSnapshot,
    )