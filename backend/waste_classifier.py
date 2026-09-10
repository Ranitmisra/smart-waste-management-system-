def classify_waste(waste_name: str):

    waste_name = waste_name.lower().strip()

    # Wet Waste
    wet_waste = [
        "banana",
        "apple",
        "orange",
        "fruit",
        "fruits",
        "vegetable",
        "vegetables",
        "food",
        "food waste",
        "vegetable peels",
        "fruit peels"
    ]

    # Dry Waste
    dry_waste = [
        "plastic",
        "plastic bottle",
        "bottle",
        "plastic bag",
        "paper",
        "newspaper",
        "cardboard",
        "carton",
        "glass",
        "glass bottle",
        "metal",
        "metal can",
        "tin can"
    ]

    # E-Waste
    e_waste = [
        "mobile",
        "mobile phone",
        "phone",
        "computer",
        "laptop",
        "charger",
        "keyboard",
        "mouse",
        "earphone",
        "electronic",
        "remote"
    ]

    # Hazardous Waste
    hazardous_waste = [
        "battery",
        "chemical",
        "medicine",
        "medical waste",
        "paint",
        "pesticide"
    ]

    if waste_name in wet_waste:
        return {
            "category": "Wet Waste",
            "recommended_bin": "Green Bin"
        }

    elif waste_name in dry_waste:
        return {
            "category": "Dry Waste",
            "recommended_bin": "Blue Bin"
        }

    elif waste_name in e_waste:
        return {
            "category": "E-Waste",
            "recommended_bin": "E-Waste Collection"
        }

    elif waste_name in hazardous_waste:
        return {
            "category": "Hazardous Waste",
            "recommended_bin": "Hazardous Waste Collection"
        }

    else:
        return {
            "category": "Unknown",
            "recommended_bin": "Manual Verification Required"
        }