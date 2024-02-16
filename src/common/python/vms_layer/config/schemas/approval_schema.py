post_approval_schema = {
    "type": "object",
    "properties": {
        "visitId": {"type": "string"},
        "name": {"type": "string",
                 "pattern": "^[a-zA-Z ]*$",
                 "minLength": 3,
                 "message": {
                     "required": "Name is a required property.",
                     "minLength": "Name should be atleast 3 characters long.",
                     "pattern": "Name should contain only alphabets and spaces.",
                 }},
        "organization": {"type": "string",
                         "pattern": "^[a-zA-Z0-9 ]*$",
                         "message": {
                            "required": "Organization is a required property.",
                            "pattern": "Organization should contain only alphabets, numbers and spaces.",
                         }},

        "phNumber": {"type": "string", 
                     "pattern": "^[0-9]{10}$",
                     "message": {
                         "required": "Phone number is a required property.",
                         "pattern": "Phone number should be 10 digits long.",
                     }},
        "purpose": {"type": "string",
                    "pattern": "^[a-zA-Z ]*$",
                    "message": {
                        "required": "Purpose is a required property.",
                        "pattern": "Purpose should contain only alphabets and spaces.",
                    }},
    },
    "required": ["visitId", "name", "organization", "phNumber", "purpose"],
}
patch_approval_schema = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string", 
            "enum": ["approved", "rejected"],
            "message": {
                "required": "Status is a required property.",
                "enum": "Status should be either 'approved' or 'rejected'.",
                }}
            },
    "required": ["status"],
}
