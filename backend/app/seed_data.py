from app.core.database import SessionLocal
from app.models.models import ShopperSession, Product


def seed():
    db = SessionLocal()

    if db.query(ShopperSession).count() == 0:
        sessions = [
            ShopperSession(dwell_time=90, path_length=5, gaze_shifts=8),
            ShopperSession(dwell_time=20, path_length=1, gaze_shifts=1),
            ShopperSession(dwell_time=60, path_length=2, gaze_shifts=7),
            ShopperSession(dwell_time=35, path_length=4, gaze_shifts=3),
            ShopperSession(dwell_time=45, path_length=2, gaze_shifts=2),
        ]
        db.add_all(sessions)

    if db.query(Product).count() == 0:
        products = [
            Product(name="Lays Chips", attention_duration=65, interaction_frequency=40, pickup_rate=25, conversion_rate=8, repeat_engagement=12),
            Product(name="Coca Cola", attention_duration=80, interaction_frequency=50, pickup_rate=35, conversion_rate=25, repeat_engagement=15),
            Product(name="Bread", attention_duration=30, interaction_frequency=15, pickup_rate=10, conversion_rate=8, repeat_engagement=3),
            Product(name="Maggi Noodles", attention_duration=55, interaction_frequency=35, pickup_rate=20, conversion_rate=12, repeat_engagement=8),
            Product(name="Amul Butter", attention_duration=20, interaction_frequency=10, pickup_rate=5, conversion_rate=3, repeat_engagement=2),
        ]
        db.add_all(products)

    db.commit()
    db.close()
    print("Seed data inserted.")


if __name__ == "__main__":
    seed()