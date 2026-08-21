from __future__ import annotations

import math
from typing import List, Tuple

from app.analytics.domain.attention.utils.vector_math import (
    normalize,
)

Point = Tuple[float, float]
Polygon = List[Point]


# ==========================================================
# Distance
# ==========================================================


def distance(
    first: Point,
    second: Point,
) -> float:
    """
    Euclidean distance between two points.
    """

    dx = second[0] - first[0]
    dy = second[1] - first[1]

    return math.hypot(dx, dy)


# ==========================================================
# Ray Projection
# ==========================================================


def project_ray(
    origin: Point,
    direction: Point,
    length: float,
) -> Point:
    """
    Project a ray from an origin along a direction.

    Returns the end point of the projected ray.
    """

    dx, dy = normalize(direction)

    return (
        origin[0] + dx * length,
        origin[1] + dy * length,
    )


# ==========================================================
# Point In Polygon
# ==========================================================


def point_in_polygon(
    point: Point,
    polygon: Polygon,
) -> bool:
    """
    Determine whether a point lies inside
    a polygon using the ray-casting algorithm.
    """

    inside = False

    x, y = point

    count = len(polygon)

    j = count - 1

    for i in range(count):

        xi, yi = polygon[i]
        xj, yj = polygon[j]

        intersects = (
            (yi > y) != (yj > y)
        ) and (
            x < (
                (xj - xi)
                * (y - yi)
                / ((yj - yi) + 1e-9)
                + xi
            )
        )

        if intersects:
            inside = not inside

        j = i

    return inside


# ==========================================================
# Line Intersection
# ==========================================================


def line_intersection(
    first_start: Point,
    first_end: Point,
    second_start: Point,
    second_end: Point,
) -> bool:
    """
    Determine whether two line segments intersect.
    """

    def orientation(
        a: Point,
        b: Point,
        c: Point,
    ) -> int:

        value = (
            (b[1] - a[1]) * (c[0] - b[0])
            - (b[0] - a[0]) * (c[1] - b[1])
        )

        if abs(value) < 1e-9:
            return 0

        return 1 if value > 0 else 2

    o1 = orientation(
        first_start,
        first_end,
        second_start,
    )

    o2 = orientation(
        first_start,
        first_end,
        second_end,
    )

    o3 = orientation(
        second_start,
        second_end,
        first_start,
    )

    o4 = orientation(
        second_start,
        second_end,
        first_end,
    )

    return (
        o1 != o2
        and o3 != o4
    )


# ==========================================================
# Ray / Polygon Intersection
# ==========================================================


def ray_intersects_polygon(
    origin: Point,
    end: Point,
    polygon: Polygon,
) -> bool:
    """
    Determine whether a projected ray
    intersects a polygon.
    """

    if point_in_polygon(
        origin,
        polygon,
    ):
        return True

    count = len(polygon)

    for index in range(count):

        edge_start = polygon[index]

        edge_end = polygon[
            (index + 1) % count
        ]

        if line_intersection(
            origin,
            end,
            edge_start,
            edge_end,
        ):
            return True

    return False