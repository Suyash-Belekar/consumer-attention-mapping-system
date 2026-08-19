def check_alerts(products):
    """
    Check product scores and generate alerts
    for store managers when products need attention.
    """
    alerts = []

    for product in products:
        name = product["product"]
        score = product["score"]
        rating = product["rating"]

        # Alert for poor performing products
        if score < 40:
            alerts.append({
                "type": "CRITICAL",
                "product": name,
                "message": f"{name} has a very low attractiveness score of {score}. Immediate action required.",
                "action": "Review shelf placement and pricing immediately."
            })

        # Alert for average performing products
        elif score < 60:
            alerts.append({
                "type": "WARNING",
                "product": name,
                "message": f"{name} is performing below average with a score of {score}.",
                "action": "Consider repositioning or adding promotional material."
            })

        # Alert for excellent products
        elif score >= 90:
            alerts.append({
                "type": "SUCCESS",
                "product": name,
                "message": f"{name} is performing excellently with a score of {score}.",
                "action": "Maintain current position and consider expanding stock."
            })

    return alerts


if __name__ == "__main__":
    test_products = [
        {"product": "Coca Cola", "score": 100, "rating": "Excellent"},
        {"product": "Maggi Noodles", "score": 96, "rating": "Excellent"},
        {"product": "Lays Chips", "score": 93, "rating": "Excellent"},
        {"product": "Bread", "score": 53, "rating": "Average"},
        {"product": "Amul Butter", "score": 31, "rating": "Poor"},
    ]

    alerts = check_alerts(test_products)
    print("\n=== PRODUCT ALERTS ===")
    for alert in alerts:
        print(f"\n[{alert['type']}] {alert['product']}")
        print(f"Message: {alert['message']}")
        print(f"Action: {alert['action']}")