post_approval_schema = {
    "type": "object",
    "properties": {
        "visit_id": {"type": "string"},
        "name": {"type": "string"},
        "organization": {"type": "string"},
        "ph_number": {"type": "string", "pattern": "^[0-9]{10}$"},
        "purpose": {"type": "string"},
    },
    "required": ["visit_id", "name", "organization", "ph_number", "purpose"],
}
patch_approval_schema = {
    "type": "object",
    "properties": {"status": {"type": "string", "enum": ["approved", "rejected"]}},
    "required": ["status"],
}
