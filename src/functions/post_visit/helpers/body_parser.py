"""This module contains the class to parse the request body for the post visit function."""
class Visit:
    """
    Class to parse the request body for the post visit function
    """
    def __init__(
        self, request_body, current_quarter, visitor_id, current_time, checked_in_by
    ):
        self.request_body = request_body
        self.current_quarter = current_quarter
        self.visitor_id = visitor_id
        self.current_time = current_time
        self.checked_in_by = checked_in_by

    @property
    def name(self):
        """
        Return the name of the visitor
        """
        return self.request_body["name"]

    @property
    def organization(self):
        """
        Return the organization of the visitor
        """
        return self.request_body["organization"]

    @property
    def ph_number(self):
        """
        Return the phone number of the visitor
        """
        return self.request_body["phNumber"]

    @property
    def purpose(self):
        """
        Return the purpose of the visit
        """
        return self.request_body["purpose"]

    @property
    def visit_type(self):
        """
        Return the type of the visit
        """
        return self.request_body["visitType"]

    @property
    def to_meet(self):
        """
        Return the person to meet
        """
        return self.request_body["toMeet"]

    @property
    def card_id(self):
        """
        Return the card id of the visitor
        """
        return self.request_body["cardId"]

    @property
    def comments(self):
        """
        Return the comments for the visit
        """
        return self.request_body["comments"]

    def to_object(self):
        """
        Return the parsed object
        """
        return {
            "PK": f"visit#{self.current_quarter}",
            "SK": f"visit#{self.visitor_id}#{self.current_time}",
            "name": self.name.lower(),
            "organization": self.organization.lower(),
            "phNumber": self.ph_number,
            "purpose": self.purpose,
            "checkedInBy": self.checked_in_by.lower(),
            "visitType": self.visit_type,
            "checkInTime": str(self.current_time),
            "toMeet": self.to_meet.lower(),
            "cardId": self.card_id,
            "comments": self.comments.lower() if self.comments else None,
        }
