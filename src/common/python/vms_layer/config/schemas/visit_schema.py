post_visit_schema = {
    "type": "object",
    "properties": {
        "visitorId": {
            "type": "string",
            "message": {
                "required": "Visitor id is a required property.",
            }},
        "name": {
            "type": "string", 
            "pattern": "^[A-Za-z0-9 ]+$",
            "message": {
                "required": "Name is a required property.",
                "pattern": "Name should contain only alphabets and spaces.",
            }},
        "organization": {
            "type": "string", 
            "pattern": "^[A-Za-z0-9 ]+$",
            "message": {
                "required": "Organization is a required property.",
                "pattern": "Organization should contain only alphabets, numbers and spaces.",
            }},
        "phNumber": {
            "type": "string", 
            "pattern": "^[0-9]+$",
            "message": {
                "required": "Phone number is a required property.",
                "pattern": "Phone number should contain only numbers.",
            }},
        "purpose": {
            "type": "string", 
            "pattern": "^[A-Za-z0-9 ]+$",
            "message": {
                "required": "Purpose is a required property.",
                "pattern": "Purpose should contain only alphabets, numbers and spaces.",
            }},
        "visitType": {
            "type": "string", 
            "enum": ["inside_office", "outside_office"],
            "message": {
                "required": "Visit type is a required property.",
                "enum": "Visit type should be either 'inside_office' or 'outside_office'.",
            }},
        "toMeet": {
            "type": "string", 
            "pattern": "^[A-Za-z0-9 ]+$",
            "message": {
                "required": "To meet is a required property.",
                "pattern": "To meet should contain only alphabets, numbers and spaces.",
            }},
        "cardId": {
            "type": "string", 
            "pattern": "^[A-Za-z0-9]+$",
            "message": {
                "required": "Card id is a required property.",
                "pattern": "Card id should contain only alphabets and numbers.",
            }},
        "comments": {
            "type": "string", 
            "pattern": "^[A-Za-z0-9 ]*$",
            "message": {
                "required": "Comments is a required property.",
                "pattern": "Comments should contain only alphabets, numbers and spaces.",
            }},
    },
    "required": [
        "visitorId",
        "purpose",
        "visitType",
        "toMeet",
        "name",
        "organization",
        "phNumber",
    ],
}
