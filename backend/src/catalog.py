import json
from datetime import datetime

# Local Catalog Dataset for Sharma General Store, Laxmi Nagar, Delhi
# Timestamp: Rates updated daily at 9:00 AM IST
CATALOG_DATA = [
    {
        "id": "prod_1",
        "name": "Aashirvaad Shuddh Chakki Atta",
        "aliases": ["atta", "aata", "wheat flour", "aashirvaad atta"],
        "category": "Groceries",
        "unit": "5 kg",
        "price": 235.0,
        "in_stock": True,
        "stock_count": 15,
        "last_updated": "Aaj subah 9:00 AM (Today 9:00 AM IST)"
    },
    {
        "id": "prod_2",
        "name": "Aashirvaad Shuddh Chakki Atta 10kg",
        "aliases": ["10kg atta", "large atta"],
        "category": "Groceries",
        "unit": "10 kg",
        "price": 450.0,
        "in_stock": True,
        "stock_count": 8,
        "last_updated": "Aaj subah 9:00 AM (Today 9:00 AM IST)"
    },
    {
        "id": "prod_3",
        "name": "Fortune Sunlite Sunflower Oil",
        "aliases": ["sunflower oil", "oil", "tel", "fortune oil"],
        "category": "Edible Oil",
        "unit": "1 Litre",
        "price": 145.0,
        "in_stock": True,
        "stock_count": 20,
        "last_updated": "Aaj subah 9:00 AM (Today 9:00 AM IST)"
    },
    {
        "id": "prod_4",
        "name": "Fortune Kachi Ghani Mustard Oil",
        "aliases": ["mustard oil", "sarson tel", "sarson ka tel"],
        "category": "Edible Oil",
        "unit": "1 Litre",
        "price": 155.0,
        "in_stock": True,
        "stock_count": 12,
        "last_updated": "Aaj subah 9:00 AM (Today 9:00 AM IST)"
    },
    {
        "id": "prod_5",
        "name": "Sugar (Refined Cheeni)",
        "aliases": ["sugar", "cheeni", "chini"],
        "category": "Groceries",
        "unit": "1 kg",
        "price": 44.0,
        "in_stock": True,
        "stock_count": 50,
        "last_updated": "Aaj subah 9:00 AM (Today 9:00 AM IST)"
    },
    {
        "id": "prod_6",
        "name": "Tata Salt (Iodized)",
        "aliases": ["tata salt", "namak", "salt"],
        "category": "Groceries",
        "unit": "1 kg",
        "price": 28.0,
        "in_stock": True,
        "stock_count": 40,
        "last_updated": "Aaj subah 9:00 AM (Today 9:00 AM IST)"
    },
    {
        "id": "prod_7",
        "name": "Tata Tea Gold",
        "aliases": ["tata tea", "chai patti", "tea", "chai"],
        "category": "Beverages",
        "unit": "250 gram",
        "price": 160.0,
        "in_stock": True,
        "stock_count": 18,
        "last_updated": "Aaj subah 9:00 AM (Today 9:00 AM IST)"
    },
    {
        "id": "prod_8",
        "name": "Maggi 2-Minute Noodles (4 Pack)",
        "aliases": ["maggi", "maggie", "noodles"],
        "category": "Snacks",
        "unit": "4 Pack (280g)",
        "price": 56.0,
        "in_stock": True,
        "stock_count": 30,
        "last_updated": "Aaj subah 9:00 AM (Today 9:00 AM IST)"
    },
    {
        "id": "prod_9",
        "name": "Amul Taaza Toned Milk",
        "aliases": ["amul milk", "doodh", "milk", "taaza milk"],
        "category": "Dairy",
        "unit": "1 Litre",
        "price": 54.0,
        "in_stock": True,
        "stock_count": 25,
        "last_updated": "Aaj subah 9:00 AM (Today 9:00 AM IST)"
    },
    {
        "id": "prod_10",
        "name": "Parle-G Biscuits",
        "aliases": ["parle g", "biscuit", "parleg"],
        "category": "Snacks",
        "unit": "80 gram",
        "price": 10.0,
        "in_stock": True,
        "stock_count": 60,
        "last_updated": "Aaj subah 9:00 AM (Today 9:00 AM IST)"
    },
    {
        "id": "prod_11",
        "name": "Britannia Good Day Cashew Cookies",
        "aliases": ["good day", "goodday", "cashew biscuit"],
        "category": "Snacks",
        "unit": "200 gram",
        "price": 40.0,
        "in_stock": False,  # Out of stock to test graceful handling!
        "stock_count": 0,
        "last_updated": "Aaj subah 9:00 AM (Today 9:00 AM IST)"
    },
    {
        "id": "prod_12",
        "name": "Surf Excel Easy Wash Powder",
        "aliases": ["surf excel", "surf", "detergent", "washing powder"],
        "category": "Household",
        "unit": "1 kg",
        "price": 140.0,
        "in_stock": True,
        "stock_count": 10,
        "last_updated": "Aaj subah 9:00 AM (Today 9:00 AM IST)"
    }
]

def search_product(query: str):
    """
    Search catalog by product name or keywords.
    Returns product details including unit price, stock status, and last_updated timestamp.
    """
    if not query:
        return {"status": "error", "message": "Search query cannot be empty."}

    q = query.lower().strip()
    results = []

    for prod in CATALOG_DATA:
        # Check exact or partial matches in name or aliases
        if q in prod["name"].lower() or any(q in alias for alias in prod["aliases"]):
            results.append(prod)

    if results:
        return {
            "status": "found",
            "matches_count": len(results),
            "products": results,
            "data_source": "Sharma General Store Live Inventory",
            "rates_valid_as_of": "Aaj subah 9:00 AM (Today 9:00 AM IST)"
        }
    
    return {
        "status": "not_found",
        "query": query,
        "message": f"Product '{query}' is currently not listed in Sharma General Store catalog.",
        "contact_seller": "Ramesh Sharma - 98765 43210"
    }

def calculate_order_total(items_input):
    """
    Calculate total bill for a list of items.
    Each item can specify name/alias and quantity.
    Returns itemized breakdown, subtotal, delivery fee, total, and estimated delivery window.
    """
    if isinstance(items_input, str):
        try:
            items_input = json.loads(items_input)
        except json.JSONDecodeError:
            # Simple fallback if passed as text
            items_input = [{"name": items_input, "quantity": 1}]

    item_breakdown = []
    subtotal = 0.0

    for entry in items_input:
        name = entry.get("name", "") if isinstance(entry, dict) else str(entry)
        qty = float(entry.get("quantity", 1)) if isinstance(entry, dict) else 1.0
        
        search_res = search_product(name)
        if search_res["status"] == "found":
            matched_prod = search_res["products"][0]
            unit_price = matched_prod["price"]
            item_cost = unit_price * qty
            subtotal += item_cost
            item_breakdown.append({
                "product_name": matched_prod["name"],
                "unit": matched_prod["unit"],
                "unit_price": unit_price,
                "quantity": qty,
                "total_item_price": item_cost,
                "in_stock": matched_prod["in_stock"]
            })
        else:
            item_breakdown.append({
                "product_name": name,
                "status": "unlisted_or_not_found",
                "unit_price": 0.0,
                "quantity": qty,
                "total_item_price": 0.0,
                "in_stock": False
            })

    # Home delivery rules: Free above 500, else 30
    delivery_fee = 0.0 if subtotal >= 500.0 else 30.0
    final_total = subtotal + delivery_fee if subtotal > 0 else 0.0

    return {
        "status": "success",
        "items": item_breakdown,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "delivery_rule": "Free delivery above ₹500, else ₹30 delivery fee",
        "final_total": final_total,
        "estimated_delivery": "2 to 3 hours",
        "rates_valid_as_of": "Aaj subah 9:00 AM (Today 9:00 AM IST)"
    }
