from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Tuple

BoundingBox = Tuple[int, int, int, int]
Point2D = Tuple[int, int]


@dataclass(slots=True)
class FrameData:
    """One fully processed frame and its reusable pipeline outputs."""
    frame: Any
    frame_number: int
    timestamp: float
    detections: list["Detection"] = field(default_factory=list)
    tracked_people: list["TrackedPerson"] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class Detection:
    bbox: BoundingBox
    confidence: float
    class_id: int

    @property
    def width(self) -> int:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> int:
        return self.bbox[3] - self.bbox[1]

    @property
    def area(self) -> int:
        return self.width * self.height

    @property
    def center(self) -> Point2D:
        return ((self.bbox[0] + self.bbox[2]) // 2, (self.bbox[1] + self.bbox[3]) // 2)


@dataclass(slots=True)
class TrackedPerson:
    """A tracked shopper enriched with mapping context for downstream analytics."""
    track_id: int
    bbox: BoundingBox
    confidence: float
    timestamp: float
    store_id: Any | None = None
    camera_id: str | None = None
    zone_id: Any | None = None
    shelf_id: Any | None = None
    product_id: Any | None = None

    @property
    def shopper_id(self) -> int:
        return self.track_id

    @property
    def id(self) -> int:
        return self.track_id

    def __getitem__(self, key: str) -> Any:
        aliases = {
            "shopper_id": self.track_id,
            "track_id": self.track_id,
            "id": self.track_id,
            "bbox": self.bbox,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "store_id": self.store_id,
            "camera_id": self.camera_id,
            "zone_id": self.zone_id,
            "shelf_id": self.shelf_id,
            "product_id": self.product_id,
        }
        if key not in aliases:
            raise KeyError(f"'TrackedPerson' object has no key '{key}'")
        return aliases[key]

    @property
    def center(self) -> Point2D:
        return ((self.bbox[0] + self.bbox[2]) // 2, (self.bbox[1] + self.bbox[3]) // 2)

    @property
    def width(self) -> int:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> int:
        return self.bbox[3] - self.bbox[1]

    @property
    def area(self) -> int:
        return self.width * self.height


@dataclass(slots=True)
class TrackingResult:
    frame: Any
    frame_number: int
    timestamp: float
    detections: list[Detection] = field(default_factory=list)
    tracked_people: list[TrackedPerson] = field(default_factory=list)
