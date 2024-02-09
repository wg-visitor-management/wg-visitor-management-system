card_schema = {
    "type": "array",
    "properties": {
        "card_id": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9]+$",
            "message": {
                "required": "Card id is a required property.",
                "pattern": "Card id should contain only alphabets and numbers.",
            },
        },
    },
    "required": ["card_id"],
}

card_update_schema = {
    "type": "object",
    "properties": {
        "visitId": {"type": "string"},
        "status": {"type": "string", 
                   "enum": ["available", "occupied", "discarded"],
                     "message": {
                          "required": "Status is a required property.",
                          "enum": "Status should be either 'available', 'occupied' or 'discarded'.",
                     }
                   },
    },
    "required": ["status"],
}
