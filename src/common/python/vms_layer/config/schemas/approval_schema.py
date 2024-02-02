post_approval_schema = {
    "type": "object",
    "properties": {
        "visit_id": {
            "type": "string"
        }
    },
    "required": ["visit_id"]
}
patch_approval_schema = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["approved", "rejected"]
        }
    },
    "required": ["status"]
}