

def parse_request_body_to_object(request_body, visitor_id, picture_name_self, picture_name_id):
    body = {}
    
    body["PK"] = "visitor"
    body["SK"] = visitor_id
    body["firstName"] = request_body["firstName"]
    body["lastName"] = request_body["lastName"]
    body["phoneNumber"] = request_body["phoneNumber"]
    body["email"] = request_body["email"]
    body["organisation"] = request_body["organisation"]
    body["address"] = request_body["address"]
    body["idProofNumber"] = request_body["idProofNumber"]
    body["profilePictureUrl"] = picture_name_self
    body["idProofPictureUrl"] = picture_name_id

    return body