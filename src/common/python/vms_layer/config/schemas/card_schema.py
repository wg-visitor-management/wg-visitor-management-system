card_schema = {
    "type": "object",
    "properties": {
        "cardId": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9]*$",
            },
    },
    "required": ["cardId"],
}

card_update_schema = {
    "type": "object",
    "properties": {
        "visitId": {"type": "string"},
        "status": {
            "type": "string",
            "enum": ["available", "occupied", "discarded"]
        }
    },
    "required": ["visitId", "status"]
}
