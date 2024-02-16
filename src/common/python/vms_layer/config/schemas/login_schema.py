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
            "minLength": 8,
            "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$",
            "message": {
                "required": "Password is a required property.",
                "minLength": "Password should be atleast 8 characters long.", 
                "pattern": "Password should contain atleast one uppercase letter, one lowercase letter, one number and one special character."
                }},
    },
    "required": ["username", "password"],
}