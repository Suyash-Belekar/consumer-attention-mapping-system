from __future__ import annotations

import math
from typing import Tuple


Vector2D = Tuple[float, float]
Vector3D = Tuple[float, float, float]


# ==========================================================
# Basic Vector Operations
# ==========================================================


def magnitude(vector: Vector2D) -> float:
    """
    Compute the magnitude of a 2D vector.
    """

    x, y = vector

    return math.sqrt(x * x + y * y)


def normalize(vector: Vector2D) -> Vector2D:
    """
    Normalize a 2D vector.
    """

    length = magnitude(vector)

    if length == 0:
        return (0.0, 0.0)

    x, y = vector

    return (
        x / length,
        y / length,
    )


# ==========================================================
# Dot Product
# ==========================================================


def dot(
    first: Vector2D,
    second: Vector2D,
) -> float:
    """
    Compute the dot product of two vectors.
    """

    return (
        first[0] * second[0]
        + first[1] * second[1]
    )


# ==========================================================
# Cross Product
# ==========================================================


def cross(
    first: Vector2D,
    second: Vector2D,
) -> float:
    """
    Compute the 2D cross product.
    """

    return (
        first[0] * second[1]
        - first[1] * second[0]
    )


# ==========================================================
# Angle
# ==========================================================


def angle_between(
    first: Vector2D,
    second: Vector2D,
) -> float:
    """
    Compute the angle (degrees)
    between two vectors.
    """

    first = normalize(first)

    second = normalize(second)

    cosine = dot(
        first,
        second,
    )

    cosine = max(
        -1.0,
        min(1.0, cosine),
    )

    return math.degrees(
        math.acos(cosine)
    )


# ==========================================================
# Rotation
# ==========================================================


def rotate(
    vector: Vector2D,
    angle_degrees: float,
) -> Vector2D:
    """
    Rotate a vector around the origin.
    """

    radians = math.radians(
        angle_degrees
    )

    cosine = math.cos(radians)

    sine = math.sin(radians)

    x, y = vector

    return (
        x * cosine - y * sine,
        x * sine + y * cosine,
    )


# ==========================================================
# Direction Vector
# ==========================================================


def direction_from_angles(
    yaw: float,
    pitch: float,
) -> Vector3D:
    """
    Convert yaw and pitch into
    a normalized 3D direction vector.

    Roll is ignored because it does not
    affect the viewing direction.
    """

    yaw = math.radians(yaw)

    pitch = math.radians(pitch)

    x = math.sin(yaw) * math.cos(pitch)

    y = -math.sin(pitch)

    z = math.cos(yaw) * math.cos(pitch)

    length = math.sqrt(
        x * x +
        y * y +
        z * z
    )

    if length == 0:
        return (
            0.0,
            0.0,
            1.0,
        )

    return (
        x / length,
        y / length,
        z / length,
    )