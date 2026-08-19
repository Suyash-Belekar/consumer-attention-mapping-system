def classify_shopper(dwell_time, path_length, gaze_shifts):
    """
    Classify shopper behavior based on tracking metrics.
    
    dwell_time: total time spent in store (seconds)
    path_length: number of zones visited
    gaze_shifts: number of times gaze direction changed
    """
    
    # Explorer: high movement + high dwell time
    if path_length >= 4 and dwell_time >= 60:
        segment = "Explorer"
        description = "Browses the entire store with no fixed plan"
    
    # Quick Buyer: short path + fast exit
    elif path_length <= 2 and dwell_time <= 30:
        segment = "Quick Buyer"
        description = "Knows what they want, in and out fast"
    
    # Comparison Shopper: long dwell + high gaze shifts
    elif dwell_time >= 45 and gaze_shifts >= 5:
        segment = "Comparison Shopper"
        description = "Spends time comparing products before deciding"
    
    # Impulse Buyer: moderate dwell + moderate path
    elif path_length >= 3 and dwell_time <= 45:
        segment = "Impulse Buyer"
        description = "Buys things they did not plan to"
    
    # Brand Loyal: short path + long dwell in specific zone
    else:
        segment = "Brand Loyal Customer"
        description = "Always goes to the same brand or shelf"
    
    return {
        "segment": segment,
        "description": description,
        "dwell_time": dwell_time,
        "path_length": path_length,
        "gaze_shifts": gaze_shifts
    }


def segment_shoppers(shopper_sessions):
    """
    Segment a list of shopper sessions.
    Each session: {"id": 1, "dwell_time": 45, "path_length": 3, "gaze_shifts": 4}
    """
    results = []
    for session in shopper_sessions:
        result = classify_shopper(
            dwell_time=session.get("dwell_time", 0),
            path_length=session.get("path_length", 1),
            gaze_shifts=session.get("gaze_shifts", 0)
        )
        result["shopper_id"] = session.get("id")
        results.append(result)
    return results


# Test it directly
if __name__ == "__main__":
    test_sessions = [
        {"id": 1, "dwell_time": 90, "path_length": 5, "gaze_shifts": 8},
        {"id": 2, "dwell_time": 20, "path_length": 1, "gaze_shifts": 1},
        {"id": 3, "dwell_time": 60, "path_length": 2, "gaze_shifts": 7},
        {"id": 4, "dwell_time": 35, "path_length": 4, "gaze_shifts": 3},
        {"id": 5, "dwell_time": 45, "path_length": 2, "gaze_shifts": 2},
    ]
    
    results = segment_shoppers(test_sessions)
    for r in results:
        print(f"Shopper #{r['shopper_id']} → Segment: {r['segment']} | {r['description']}")