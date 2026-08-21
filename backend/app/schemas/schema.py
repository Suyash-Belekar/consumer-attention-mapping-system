from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum

class BehavioralSegment(str, Enum):
    EXPLORER = "Explorer"
    QUICK_BUYER = "Quick Buyer"
    COMPARISON_SHOPPER = "Comparison Shopper"
    IMPULSE_BUYER = "Impulse Buyer"
    BRAND_LOYAL = "Brand Loyal"

class BehavioralTagRequest(BaseModel):
    session_id: str
    path_length: float = Field(..., description="Total distance walked in store")
    total_dwell_time: float = Field(..., description="Total time spent in seconds")
    head_gaze_shifts: int = Field(..., description="Number of gaze direction changes")

class BehavioralTagResponse(BaseModel):
    session_id: str
    behavioral_segment: BehavioralSegment
    updated_at: datetime

class ProductAttractivenessScore(BaseModel):
    product_id: str
    shelf_id: str
    attention_duration_score: float = Field(..., ge=0, le=100)
    interaction_freq_score: float = Field(..., ge=0, le=100)
    pickup_rate_score: float = Field(..., ge=0, le=100)
    conversion_rate_score: float = Field(..., ge=0, le=100)
    repeat_engagement_score: float = Field(..., ge=0, le=100)
    composite_attractiveness_score: float = Field(..., ge=0, le=100)

class RecommendationItem(BaseModel):
    code: str
    severity: str
    message: str

class ProductAnalysisResponse(BaseModel):
    product_id: str
    attractiveness_score: float
    metrics_breakdown: Dict[str, float]
    recommendations: List[RecommendationItem]