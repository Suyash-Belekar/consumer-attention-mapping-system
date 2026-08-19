def calculate_attractiveness_score(
    attention_duration,
    interaction_frequency,
    pickup_rate,
    conversion_rate,
    repeat_engagement,
    store_avg_attention=50,
    store_avg_interaction=30,
    store_avg_pickup=20,
    store_avg_conversion=15,
    store_avg_repeat=10
):
    """
    Calculate Product Attractiveness Score using weighted formula:
    Score = (Attention Duration x 0.35) + (Interaction Freq x 0.25)
          + (Pickup Rate x 0.20) + (Conversion Rate x 0.15)
          + (Repeat Engagement x 0.05)
    All inputs are normalized relative to store averages.
    Output: 0 to 100
    """

    # Normalize each metric relative to store average (0-100 scale)
    norm_attention = min((attention_duration / store_avg_attention) * 100, 100)
    norm_interaction = min((interaction_frequency / store_avg_interaction) * 100, 100)
    norm_pickup = min((pickup_rate / store_avg_pickup) * 100, 100)
    norm_conversion = min((conversion_rate / store_avg_conversion) * 100, 100)
    norm_repeat = min((repeat_engagement / store_avg_repeat) * 100, 100)

    # Apply weighted formula
    score = (
        (norm_attention * 0.35) +
        (norm_interaction * 0.25) +
        (norm_pickup * 0.20) +
        (norm_conversion * 0.15) +
        (norm_repeat * 0.05)
    )

    return round(score, 2)


def score_products(products):
    """
    Score a list of products.
    Each product: {
        "name": "Product A",
        "attention_duration": 45,
        "interaction_frequency": 20,
        "pickup_rate": 15,
        "conversion_rate": 10,
        "repeat_engagement": 5
    }
    """
    results = []
    for product in products:
        score = calculate_attractiveness_score(
            attention_duration=product.get("attention_duration", 0),
            interaction_frequency=product.get("interaction_frequency", 0),
            pickup_rate=product.get("pickup_rate", 0),
            conversion_rate=product.get("conversion_rate", 0),
            repeat_engagement=product.get("repeat_engagement", 0)
        )
        results.append({
            "product": product["name"],
            "score": score,
            "rating": "Excellent" if score >= 80 else "Good" if score >= 60 else "Average" if score >= 40 else "Poor"
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


if __name__ == "__main__":
    test_products = [
        {"name": "Lays Chips", "attention_duration": 65, "interaction_frequency": 40, "pickup_rate": 25, "conversion_rate": 18, "repeat_engagement": 12},
        {"name": "Coca Cola", "attention_duration": 80, "interaction_frequency": 50, "pickup_rate": 35, "conversion_rate": 25, "repeat_engagement": 15},
        {"name": "Bread", "attention_duration": 30, "interaction_frequency": 15, "pickup_rate": 10, "conversion_rate": 8, "repeat_engagement": 3},
        {"name": "Maggi Noodles", "attention_duration": 55, "interaction_frequency": 35, "pickup_rate": 20, "conversion_rate": 12, "repeat_engagement": 8},
        {"name": "Amul Butter", "attention_duration": 20, "interaction_frequency": 10, "pickup_rate": 5, "conversion_rate": 3, "repeat_engagement": 2},
    ]

    results = score_products(test_products)
    print("\n=== PRODUCT ATTRACTIVENESS SCORES ===")
    for r in results:
        print(f"{r['product']:20} Score: {r['score']:6.2f} | Rating: {r['rating']}")