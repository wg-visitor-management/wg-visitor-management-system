post_visit_schema = {
    "type": "object",
    "properties": {
        "visitorId": {"type": "string"},
        "name": {"type": "string", "pattern": "^[A-Za-z0-9 ]+$"},
        "organization": {"type": "string", "pattern": "^[A-Za-z0-9 ]+$"},
        "phNumber": {"type": "string", "pattern": "^[0-9]+$"},
        "purpose": {"type": "string", "pattern": "^[A-Za-z0-9]+$"},
        "visitType": {"type": "string", "enum": ["inside_office", "outside_office"]},
        "toMeet": {"type": "string", "pattern": "^[A-Za-z0-9 ]+$"},
        "cardId": {"type": "string", "pattern": "^[A-Za-z0-9]+$"},
        "comments": {"type": "string", "pattern": "^[A-Za-z0-9 ]+$"},
    },
    "required": [
        "visitorId",
        "purpose",
        "visitType",
        "toMeet",
        "name",
        "organization",
        "phNumber",
    ],
}
