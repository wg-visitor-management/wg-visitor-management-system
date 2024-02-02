card_schema = {
    "type": "object",
    "properties": {
        "card_id": {"type": "string"},
    },
    "required": ["card_id"],
}

card_update_schema = {
    "type": "object",
    "properties": {
        "visit_id": {"type": "string"},
        "status": {
            "type": "string",
            "enum": ["available", "occupied", "discarded"]
        }
    },
    "required": ["visit_id", "status"]
}
