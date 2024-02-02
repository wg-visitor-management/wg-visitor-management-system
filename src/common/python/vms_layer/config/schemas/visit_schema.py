post_visit_schema = {
    "type": "object",
    "properties": {
        "visitor_id": {"type": "string"},
        "name": {"type": "string", "pattern": "^[A-Za-z0-9 ]+$"},
        "organization": {"type": "string", "pattern": "^[A-Za-z0-9 ]+$"},
        "ph_number": {"type": "string", "pattern": "^[0-9]+$"},
        "purpose": {"type": "string", "pattern": "^[A-Za-z0-9]+$"},
        "visit_type": {"type": "string", "enum": ["inside_office", "outside_office"]},
        "to_meet": {"type": "string", "pattern": "^[A-Za-z0-9 ]+$"},
        "card_id": {"type": "string", "pattern": "^[A-Za-z0-9]+$"},
        "comments": {"type": "string", "pattern": "^[A-Za-z0-9 ]+$"},
    },
    "required": [
        "visitor_id",
        "purpose",
        "visit_type",
        "to_meet",
        "name",
        "organization",
        "ph_number",
    ],
}
