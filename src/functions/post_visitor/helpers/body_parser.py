"""
This module contains the Body class 
which is used to parse the request body and return the required fields.
"""

class Body:
    """
    Class to parse the request body for the post visitor function
    """
    def __init__(self, request_body, picture_name_self, picture_name_id):
        self.request_body = request_body
        self.picture_name_self = picture_name_self
        self.picture_name_id = picture_name_id

    @property
    def firstname(self):
        """
        Return the first name of the visitor
        """
        return self.request_body.get("firstName")
    @property
    def lastname(self):
        """
        Return the last name of the visitor
        """
        return self.request_body.get("lastName")
    @property
    def phonenumber(self):
        """
        Return the phone number of the visitor
        """
        return self.request_body.get("phoneNumber")
    @property
    def email(self):
        """
        Return the email of the visitor
        """
        return self.request_body.get("email")
    @property
    def organization(self):
        """
        Return the organization of the visitor
        """
        return self.request_body.get("organization")
    @property
    def address(self):
        """
        Return the address of the visitor
        """
        return self.request_body.get("address")
    @property
    def idproofnumber(self):
        """
        Return the id proof number of the visitor
        """
        return self.request_body.get("idProofNumber")
    @property
    def profilepictureurl(self):
        """
        Return the profile picture url of the visitor
        """
        return self.picture_name_self
    @property
    def idproofpictureurl(self):
        """
        Return the id proof picture url of the visitor
        """
        return self.picture_name_id

    def to_object(self):
        """
        Return the visitor object
        """
        return {
            "firstName": self.firstname,
            "lastName": self.lastname,
            "phoneNumber": self.phonenumber,
            "email": self.email,
            "organization": self.organization,
            "address": self.address,
            "idProofNumber": self.idproofnumber,
            "profilePictureUrl": self.profilepictureurl,
            "idProofPictureUrl": self.idproofpictureurl
        }
