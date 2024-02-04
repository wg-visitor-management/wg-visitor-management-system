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
