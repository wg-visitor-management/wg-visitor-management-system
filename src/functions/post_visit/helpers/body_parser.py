class Visit:
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
        return self.request_body["name"]

    @property
    def organization(self):
        return self.request_body["organization"]

    @property
    def phNumber(self):
        return self.request_body["phNumber"]

    @property
    def purpose(self):
        return self.request_body["purpose"]

    @property
    def visit_type(self):
        return self.request_body["visitType"]

    @property
    def toMeet(self):
        return self.request_body["toMeet"]

    @property
    def card_id(self):
        return self.request_body["cardId"]

    @property
    def comments(self):
        return self.request_body["comments"]

    def to_object(self):
        return {
            "PK": f"visit#{self.current_quarter}",
            "SK": f"visit#{self.visitor_id}#{self.current_time}",
            "name": self.name.lower(),
            "organization": self.organization.lower(),
            "phNumber": self.phNumber,
            "purpose": self.purpose,
            "checkedInBy": self.checked_in_by.lower(),
            "visitType": self.visit_type,
            "checkInTime": str(self.current_time),
            "toMeet": self.toMeet.lower(),
            "cardId": self.card_id,
            "comments": self.comments.lower() if self.comments else None,
        }
