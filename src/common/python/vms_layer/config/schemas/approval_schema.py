post_approval_schema = {
    "type": "object",
    "properties": {
        "visitId": {"type": "string"},
        "name": {"type": "string"},
        "organization": {"type": "string"},
        "phNumber": {"type": "string", "pattern": "^[0-9]{10}$"},
        "purpose": {"type": "string"},
    },
    "required": ["visitId", "name", "organization", "phNumber", "purpose"],
}
patch_approval_schema = {
    "type": "object",
    "properties": {"status": {"type": "string", "enum": ["approved", "rejected"]}},
    "required": ["status"],
}
