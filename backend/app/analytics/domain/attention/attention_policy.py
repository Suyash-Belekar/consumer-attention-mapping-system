from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class AttentionPolicy:
    """
    Configuration values for the attention analytics subsystem.

    All thresholds and tuning parameters are centralized here
    to simplify calibration and testing.
    """

    # ==========================================================
    # Face Detection
    # ==========================================================

    # Percentage of the person's bounding box used for face cropping.
    face_crop_ratio: float = 0.40

    # Minimum confidence required for a valid face detection.
    minimum_face_confidence: float = 0.60

    # ==========================================================
    # Head Pose
    # ==========================================================

    # Minimum confidence required to accept a head pose estimate.
    minimum_head_pose_confidence: float = 0.50

    # Maximum allowable head rotation (degrees).
    maximum_yaw: float = 60.0
    maximum_pitch: float = 45.0
    maximum_roll: float = 45.0

    # ==========================================================
    # Gaze Projection
    # ==========================================================

    # Length of the projected gaze ray in image pixels.
    projection_distance: float = 500.0

    # ==========================================================
    # Attention Session
    # ==========================================================

    # Minimum time (seconds) before an attention session is considered valid.
    minimum_attention_duration: float = 0.50

    # Maximum time (seconds) a track can disappear before closing a session.
    session_timeout: float = 1.00

    # ==========================================================
    # Shelf Matching
    # ==========================================================

    # Maximum pixel distance allowed when associating a projected
    # gaze point with a shelf polygon.
    shelf_match_threshold: float = 50.0

    # ==========================================================
    # Debugging
    # ==========================================================

    enable_debug_logging: bool = False

    draw_face_box: bool = True

    draw_head_pose: bool = True

    draw_gaze_projection: bool = True