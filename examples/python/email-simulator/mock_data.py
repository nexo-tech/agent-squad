# Mock data for e-commerce support simulator
# Based on examples/ecommerce-support-simulator/resources/ui/public/mock_data.json

ORDERS = {
    "12345": {
        "status": "Shipped",
        "items": ["Widget A", "Gadget B"],
        "total": 150.0,
        "customer_email": "john.doe@example.com",
        "order_date": "2024-01-15"
    },
    "67890": {
        "status": "Processing",
        "items": ["Gizmo C"],
        "total": 75.5,
        "customer_email": "jane.smith@example.com",
        "order_date": "2024-01-18"
    },
    "11111": {
        "status": "Delivered",
        "items": ["Super Device X", "Accessory Y", "Cable Z"],
        "total": 299.99,
        "customer_email": "bob.wilson@example.com",
        "order_date": "2024-01-10"
    },
    "22222": {
        "status": "Pending",
        "items": ["Premium Package"],
        "total": 499.0,
        "customer_email": "alice.jones@example.com",
        "order_date": "2024-01-20"
    }
}

SHIPMENTS = {
    "12345": {
        "carrier": "FastShip",
        "tracking_number": "FS123456789",
        "status": "In Transit",
        "estimated_delivery": "2024-01-22",
        "last_location": "Distribution Center, Chicago, IL"
    },
    "11111": {
        "carrier": "QuickDeliver",
        "tracking_number": "QD987654321",
        "status": "Delivered",
        "delivered_date": "2024-01-14",
        "signed_by": "B. Wilson"
    }
}

PRODUCTS = {
    "Widget A": {
        "description": "High-quality widget for everyday use",
        "price": 49.99,
        "category": "Electronics",
        "in_stock": True
    },
    "Gadget B": {
        "description": "Advanced gadget with smart features",
        "price": 99.99,
        "category": "Electronics",
        "in_stock": True
    },
    "Gizmo C": {
        "description": "Compact gizmo for professionals",
        "price": 75.50,
        "category": "Tools",
        "in_stock": False
    },
    "Super Device X": {
        "description": "Top-of-the-line device with premium features",
        "price": 199.99,
        "category": "Electronics",
        "in_stock": True
    }
}


def order_lookup(order_id: str) -> dict:
    """Retrieve order details from the database."""
    if order_id in ORDERS:
        return {"found": True, "order": ORDERS[order_id]}
    return {"found": False, "message": f"Order {order_id} not found"}


def shipment_tracker(order_id: str) -> dict:
    """Get real-time shipping information."""
    if order_id in SHIPMENTS:
        return {"found": True, "shipment": SHIPMENTS[order_id]}
    if order_id in ORDERS:
        return {"found": False, "message": f"No shipment information available for order {order_id}. Order status: {ORDERS[order_id]['status']}"}
    return {"found": False, "message": f"Order {order_id} not found"}


def return_processor(order_id: str) -> dict:
    """Initiate and manage return requests."""
    if order_id in ORDERS:
        order = ORDERS[order_id]
        if order["status"] == "Delivered":
            return {
                "success": True,
                "message": f"Return initiated for order {order_id}",
                "return_label": f"RET-{order_id}-2024",
                "instructions": "Please pack the items securely and drop off at any authorized shipping location."
            }
        return {
            "success": False,
            "message": f"Cannot process return for order {order_id}. Order status is '{order['status']}'. Returns are only available for delivered orders."
        }
    return {"success": False, "message": f"Order {order_id} not found"}


def product_info(product_name: str) -> dict:
    """Get product information."""
    if product_name in PRODUCTS:
        return {"found": True, "product": PRODUCTS[product_name]}
    # Try partial match
    for name, info in PRODUCTS.items():
        if product_name.lower() in name.lower():
            return {"found": True, "product": info, "product_name": name}
    return {"found": False, "message": f"Product '{product_name}' not found"}
