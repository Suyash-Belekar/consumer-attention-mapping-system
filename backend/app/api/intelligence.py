from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import User, ShopperSession, Product
from app.services.behavior import classify_shopper
from app.services.scoring import calculate_attractiveness_score
from app.services.recommendations import generate_recommendations
import base64

router = APIRouter(prefix="/api/intelligence", tags=["Behavioral Intelligence"])


@router.get("/segments")
def get_shopper_segments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Classify each shopper session and persist the segment to the DB"""
    sessions = db.query(ShopperSession).all()
    results = []

    for s in sessions:
        classification = classify_shopper(
            dwell_time=s.dwell_time,
            path_length=s.path_length,
            gaze_shifts=s.gaze_shifts
        )
        s.segment = classification["segment"]  # write back to DB
        results.append({
            "shopper_id": s.id,
            "segment": s.segment,
            "description": classification["description"],
            "dwell_time": s.dwell_time,
            "path_length": s.path_length,
            "gaze_shifts": s.gaze_shifts
        })

    db.commit()
    return {"segments": results}


@router.get("/scores")
def get_product_scores(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Score each product and persist score/rating to the DB"""
    products = db.query(Product).all()
    results = []

    for p in products:
        score = calculate_attractiveness_score(
            attention_duration=p.attention_duration,
            interaction_frequency=p.interaction_frequency,
            pickup_rate=p.pickup_rate,
            conversion_rate=p.conversion_rate,
            repeat_engagement=p.repeat_engagement
        )
        rating = "Excellent" if score >= 80 else "Good" if score >= 60 else "Average" if score >= 40 else "Poor"

        p.score = score       # write back to DB
        p.rating = rating     # write back to DB

        results.append({
            "product": p.name,
            "score": score,
            "rating": rating
        })

    db.commit()
    results.sort(key=lambda x: x["score"], reverse=True)
    return {"products": results}


@router.get("/recommendations")
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate recommendations from real product data in the DB"""
    products = db.query(Product).all()

    product_list = [
        {
            "name": p.name,
            "attention_duration": p.attention_duration,
            "pickup_rate": p.pickup_rate,
            "conversion_rate": p.conversion_rate,
            "interaction_frequency": p.interaction_frequency,
            "score": p.score or 0
        }
        for p in products
    ]

    return {"recommendations": generate_recommendations(product_list)}


@router.get("/heatmap")
def get_heatmap(
    current_user: User = Depends(get_current_user)
):
    """Generate and return heatmap as base64 image"""
    from app.services.heatmap import generate_heatmap

    heatmap_path = "heatmap.png"
    generate_heatmap(output_path=heatmap_path)

    with open(heatmap_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    return {
        "heatmap": f"data:image/png;base64,{image_data}",
        "message": "Heatmap generated successfully"
    }