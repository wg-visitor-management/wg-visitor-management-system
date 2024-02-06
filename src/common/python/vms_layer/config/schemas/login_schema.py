login_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string", 
                     "minLength": 3, 
                     "message": {
                        "required": "Username is a required property.",
                        "minLength": "Username should be atleast 3 characters long.", 
                        }},
        "password": {
            "type": "string",
            "minLength": 6, 
            "message": {
                "required": "Password is a required property.",
                "minLength": "Password should be atleast 6 characters long.", 
                }},
    },
    "required": ["username", "password"],
}