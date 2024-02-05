card_schema = {
    "type": "array",
    "properties": {
        "card_id": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9]*$",
        },
    },
    "required": ["card_id"],
}

card_update_schema = {
    "type": "object",
    "properties": {
        "visitId": {"type": "string"},
        "status": {"type": "string", "enum": ["available", "occupied", "discarded"]},
    },
    "required": ["status"],
}
