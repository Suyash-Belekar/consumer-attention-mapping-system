from __future__ import annotations

from typing import Any, Iterable

WEIGHTS = {
    "attention_duration": 0.35,
    "interaction_frequency": 0.25,
    "pickup_rate": 0.20,
    "conversion_rate": 0.15,
    "repeat_engagement": 0.05,
}
DEFAULT_REFERENCES = {
    "attention_duration": 300.0,
    "interaction_frequency": 50.0,
    "pickup_rate": 1.0,
    "conversion_rate": 1.0,
    "repeat_engagement": 10.0,
}


def _value(metrics: Any, name: str, fallback: float = 0.0) -> float:
    if name == "interaction_frequency":
        raw = getattr(metrics, "interaction_frequency", None)
        if raw is None:
            raw = getattr(metrics, "interaction_freq", fallback)
    else:
        raw = getattr(metrics, name, fallback)
    return float(raw or 0.0)


def normalize(value: float, reference: float) -> float:
    if reference <= 0:
        return 100.0 if value > 0 else 0.0
    return max(0.0, min(100.0, (float(value) / float(reference)) * 100.0))


def build_store_references(metrics_rows: Iterable[Any]) -> dict[str, float]:
    rows = list(metrics_rows)
    if not rows:
        return DEFAULT_REFERENCES.copy()

    refs = {}
    for key in WEIGHTS:
        average = sum(_value(row, key) for row in rows) / len(rows)
        floor = 0.0001 if key in {"pickup_rate", "conversion_rate"} else 1.0
        refs[key] = max(average, floor)
    return refs


def calculate_attractiveness(metrics: Any, references: dict[str, float] | None = None):
    refs = references or DEFAULT_REFERENCES
    normalized = {
        key: normalize(_value(metrics, key), refs[key])
        for key in WEIGHTS
    }
    score = sum(normalized[key] * WEIGHTS[key] for key in WEIGHTS)
    return round(max(0.0, min(100.0, score)), 2), {key: round(value, 2) for key, value in normalized.items()}


def recommendations(metrics: Any, scores: dict[str, float]) -> list[dict[str, str]]:
    pickup = _value(metrics, "pickup_rate")
    conversion = _value(metrics, "conversion_rate")
    items: list[dict[str, str]] = []

    if scores["attention_duration"] >= 80 and conversion == 0:
        items.append({
            "code": "HIGH_ATTENTION_LOW_CONVERSION",
            "severity": "HIGH",
            "message": "High eye attention but zero conversion. Review pricing, promotion, packaging or availability.",
        })
    if scores["attention_duration"] >= 75 and pickup < 0.15:
        items.append({
            "code": "HIGH_VISIBILITY_LOW_PICKUP",
            "severity": "MEDIUM",
            "message": "Customers notice the product but rarely pick it up. Review placement and merchandising.",
        })
    if pickup >= 0.50 and scores["attention_duration"] < 35:
        items.append({
            "code": "LOW_VISIBILITY_HIGH_INTERACTION",
            "severity": "MEDIUM",
            "message": "Strong interaction after discovery but low attention. Consider eye-level placement.",
        })
    if scores["interaction_frequency"] < 20:
        items.append({
            "code": "LOW_INTERACTION",
            "severity": "LOW",
            "message": "Low product interaction. Consider promotional placement or clearer product visibility.",
        })
    return items
