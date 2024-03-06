"""
Class to parse the request body for the post visitor function
"""

class Body:
    """
    Class to parse the request body for the post visitor function
    """
    def __init__(self, request_body, picture_name_self, picture_name_id):
        self.request_body = request_body
        self.picture_name_self = picture_name_self
        self.picture_name_id = picture_name_id

    def to_object(self):
        """
        Return the visitor object
        """
        return {
            "firstName": self.request_body["firstName"],
            "lastName": self.request_body["lastName"],
            "phoneNumber": self.request_body["phoneNumber"],
            "email": self.request_body["email"],
            "organization": self.request_body["organization"],
            "address": self.request_body["address"],
            "profilePictureUrl": self.picture_name_self,
            "idProofPictureUrl": self.picture_name_id
        }
