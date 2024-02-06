class Body:
    def __init__(self, request_body, picture_name_self, picture_name_id):
        self.request_body = request_body
        self.picture_name_self = picture_name_self
        self.picture_name_id = picture_name_id

    @property
    def firstname(self):
        return self.request_body["firstName"]
    @property
    def lastname(self):
        return self.request_body["lastName"]
    @property
    def phonenumber(self):
        return self.request_body["phoneNumber"]
    @property
    def email(self):
        return self.request_body["email"]
    @property
    def organization(self):
        return self.request_body["organization"]
    @property
    def address(self):
        return self.request_body["address"]
    @property
    def idproofnumber(self):
        return self.request_body["idProofNumber"]
    @property
    def profilepictureurl(self):
        return self.picture_name_self
    @property
    def idproofpictureurl(self):
        return self.picture_name_id
    
    def to_object(self):
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