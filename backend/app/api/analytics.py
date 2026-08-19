from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/attention")
def get_attention_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns aggregated attention analytics data
    for the dashboard charts
    """
    # Simulated attention data for dashboard
    # In production this comes from TimescaleDB
    attention_data = {
        "shelves": [
            {"shelf": "Aisle 1 - Snacks", "dwell_time": 45.2, "shoppers": 12},
            {"shelf": "Aisle 2 - Beverages", "dwell_time": 32.8, "shoppers": 8},
            {"shelf": "Aisle 3 - Dairy", "dwell_time": 28.5, "shoppers": 6},
            {"shelf": "Aisle 4 - Bakery", "dwell_time": 55.1, "shoppers": 15},
            {"shelf": "Aisle 5 - Frozen", "dwell_time": 19.3, "shoppers": 4},
        ],
        "total_shoppers_today": 45,
        "average_dwell_time": 36.2,
        "most_viewed_shelf": "Aisle 4 - Bakery",
    }
    return attention_data