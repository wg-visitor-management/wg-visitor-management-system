password_schema = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["get_token", "change_password"]},
        "alias": {"type": "string"},
        "code": {"type": "string", "minLength": 6, "maxLength": 6},
        "password": {"type": "string"},
    },
    "required": ["action", "alias"],
}
