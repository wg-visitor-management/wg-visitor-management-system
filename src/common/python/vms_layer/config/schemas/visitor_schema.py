visitor_schema = {
    "type": "object",
    "properties": {
        "firstName": {
            "type": "string",
            "pattern": "^[A-Za-z ]+$",
            "message": {
                "required": "First name is a required property.",
                "pattern": "First name should contain only alphabets and spaces.",
            }},
        "lastName": {
            "type": "string",
            "pattern": "^[A-Za-z ]*$",
            "message": {
                "required": "Last name is a required property.",
                "pattern": "Last name should contain only alphabets and spaces.",
            }},
        "phoneNumber": {
            "type": "string",
            "pattern": "^[0-9]{10,12}$",
            "minLength": 10,
            "message": {
                "required": "Phone number is a required property.",
                "minLength": "Phone number should be 10 digits long.",
                "pattern": "Phone number should contain only numbers.",
            }},
        "email": {
            "type": "string",
            "format": "email",
            "message": {
                "required": "Email is a required property.",
                "format": "Email should be a valid email address.",
            }},
        "organization": {
            "type": "string",
            "pattern": "^[A-Za-z0-9 ]+$",
            "message": {
                "required": "Organization is a required property.",
                "pattern": "Organization should contain only alphabets, numbers and spaces.",
            }},
        "address": {
            "type": "string",
            "pattern": "^[#.0-9a-zA-Z\s,-]*$",
            "message": {
                "required": "Address is a required property.",
                "pattern": "Address should contain only alphabets, numbers and spaces.",
            }},
        "idProofNumber": {
            "type": "string",
            "pattern": "^[A-Za-z0-9 ]*$",
            "message": {
                "required": "Id proof number is a required property.",
                "pattern": "Id proof number should contain only alphabets, numbers and spaces.",
            }},
        "idPhotoBlob": {
            "type": "string",
            "message": {
                "required": "Id photo blob is a required property.",
            }},
        "vistorPhotoBlob": {
            "type": "string",
            "message": {
                "required": "Visitor photo blob is a required property.",
            }},
    },
    "required": ["firstName", "lastName", "phoneNumber", "organization" ],
}
