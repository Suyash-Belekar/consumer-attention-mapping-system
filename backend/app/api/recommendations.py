# app/api/recommendations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.database_models import ProductAttentionModel
from app.schemas.schema import ProductAnalysisResponse, RecommendationItem

router = APIRouter(prefix="/api/products", tags=["Product Attractiveness"])

@router.get("/{product_id}/attractiveness-analysis", response_model=ProductAnalysisResponse)
async def analyze_product_performance(product_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductAttentionModel).where(ProductAttentionModel.product_id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail=f"Product ID '{product_id}' not found.")

    # Standardized Upper Bounds for Score Normalization
    MAX_ATTENTION = 300.0  # seconds
    MAX_INTERACTION = 50.0  # count

    norm_attention = min(100.0, (product.attention_duration / MAX_ATTENTION) * 100.0)
    norm_interaction = min(100.0, (product.interaction_freq / MAX_INTERACTION) * 100.0)
    norm_pickup = min(100.0, product.pickup_rate * 100.0)
    norm_conversion = min(100.0, product.conversion_rate * 100.0)
    norm_repeat = min(100.0, (product.repeat_engagement / 10.0) * 100.0)

    # Section 4.8 Weighted Formula
    composite_score = (
        (norm_attention * 0.35) +
        (norm_interaction * 0.25) +
        (norm_pickup * 0.20) +
        (norm_conversion * 0.15) +
        (norm_repeat * 0.05)
    )

    recommendations = []
    
    if norm_attention >= 75.0 and product.conversion_rate < 0.15:
        recommendations.append(RecommendationItem(
            code="HIGH_ATTENTION_LOW_CONVERSION",
            severity="HIGH",
            message="High gaze attention but low sales. Consider price sensitivity or promotional adjustment."
        ))

    if product.pickup_rate >= 0.50 and norm_attention <= 35.0:
        recommendations.append(RecommendationItem(
            code="HIGH_INTEREST_LOW_VISIBILITY",
            severity="MEDIUM",
            message="High interaction upon discovery but low overall gaze traffic. Move to eye-level position."
        ))

    return ProductAnalysisResponse(
        product_id=product_id,
        attractiveness_score=round(composite_score, 2),
        metrics_breakdown={
            "attention_score": round(norm_attention, 2),
            "interaction_score": round(norm_interaction, 2),
            "pickup_score": round(norm_pickup, 2),
            "conversion_score": round(norm_conversion, 2),
            "repeat_score": round(norm_repeat, 2)
        },
        recommendations=recommendations
    )