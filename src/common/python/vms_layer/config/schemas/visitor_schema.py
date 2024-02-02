visitor_schema = {
    "type": "object",
    "properties": {
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "phoneNumber": {"type": "string"},
        "email": {"type": "string"},
        "organisation": {"type": "string"},
        "address": {"type": "string"},
        "idProofNumber": {"type": "string"},
        "idPhotoBlob": {"type": "string"},
        "vistorPhotoBlob": {"type": "string"}
    },
    "required": ["firstName", "lastName", "phoneNumber", "email", "organisation", "address", "idProofNumber"],
}