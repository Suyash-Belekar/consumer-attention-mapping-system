def generate_recommendations(products):
    """
    Generate shelf optimization recommendations
    based on product attractiveness scores and metrics.
    """
    recommendations = []

    for product in products:
        name = product["name"]
        attention = product.get("attention_duration", 0)
        pickup = product.get("pickup_rate", 0)
        conversion = product.get("conversion_rate", 0)
        interaction = product.get("interaction_frequency", 0)
        score = product.get("score", 0)

        # Rule 1: High attention but low conversion
        if attention >= 60 and conversion <= 10:
            recommendations.append({
                "product": name,
                "issue": "High Attention but Low Sales",
                "recommendation": "Product gets high visibility but customers are not buying. Consider reviewing pricing or adding a promotional offer.",
                "priority": "High"
            })

        # Rule 2: Low attention
        elif attention <= 25:
            recommendations.append({
                "product": name,
                "issue": "Low Shelf Visibility",
                "recommendation": "Product is not getting customer attention. Move to eye-level shelf position or add better signage.",
                "priority": "High"
            })

        # Rule 3: High pickup but low conversion
        elif pickup >= 20 and conversion <= 8:
            recommendations.append({
                "product": name,
                "issue": "High Pickup but Low Purchase",
                "recommendation": "Customers pick up the product but put it back. Consider price reduction or improved packaging.",
                "priority": "Medium"
            })

        # Rule 4: Low interaction frequency
        elif interaction <= 15:
            recommendations.append({
                "product": name,
                "issue": "Low Customer Engagement",
                "recommendation": "Customers are not engaging with this product. Consider moving it near high-traffic products or running a promotion.",
                "priority": "Medium"
            })

        # Rule 5: Excellent score
        elif score >= 80:
            recommendations.append({
                "product": name,
                "issue": "Top Performing Product",
                "recommendation": "This product is performing excellently. Maintain current shelf position and consider expanding stock.",
                "priority": "Low"
            })

        # Rule 6: Average performance
        else:
            recommendations.append({
                "product": name,
                "issue": "Average Performance",
                "recommendation": "Product is performing adequately. Monitor trends and consider seasonal promotions to boost engagement.",
                "priority": "Low"
            })

    # Sort by priority
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    recommendations.sort(key=lambda x: priority_order[x["priority"]])

    return recommendations


if __name__ == "__main__":
    test_products = [
        {"name": "Lays Chips", "attention_duration": 65, "interaction_frequency": 40, "pickup_rate": 25, "conversion_rate": 8, "score": 75},
        {"name": "Coca Cola", "attention_duration": 80, "interaction_frequency": 50, "pickup_rate": 35, "conversion_rate": 25, "score": 100},
        {"name": "Bread", "attention_duration": 30, "interaction_frequency": 15, "pickup_rate": 10, "conversion_rate": 8, "score": 53},
        {"name": "Maggi Noodles", "attention_duration": 55, "interaction_frequency": 35, "pickup_rate": 20, "conversion_rate": 12, "score": 96},
        {"name": "Amul Butter", "attention_duration": 20, "interaction_frequency": 10, "pickup_rate": 5, "conversion_rate": 3, "score": 31},
    ]

    recommendations = generate_recommendations(test_products)
    print("\n=== PRODUCT RECOMMENDATIONS ===")
    for r in recommendations:
        print(f"\nProduct: {r['product']}")
        print(f"Issue: {r['issue']}")
        print(f"Recommendation: {r['recommendation']}")
        print(f"Priority: {r['priority']}")