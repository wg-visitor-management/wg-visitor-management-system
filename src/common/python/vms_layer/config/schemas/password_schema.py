password_schema = {
    "type": "object",
    "properties": {
        "action": {"type": "string", 
                   "enum": ["get_token", "change_password"],
                   "message": {
                       "required": "Action is a required property.",
                       "enum": "Action should be either 'get_token' or 'change_password'.",
                   }},
        "alias": {"type": "string"},
        "code": {"type": "string", "minLength": 6, "maxLength": 6,
                 "pattern": "^[0-9]*$",
                    "message": {
                        "required": "Code is a required property.",
                        "minLength": "Code should be 6 characters long.",
                        "maxLength": "Code should be 6 characters long.",
                        "pattern": "Code should contain only numbers.",
                 }},
        "password": {"type": "string"},
    },
    "required": ["action", "alias"],
}
