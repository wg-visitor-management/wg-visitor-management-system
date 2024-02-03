class Visit:
    def __init__(self, request_body, current_quarter, visitor_id, current_time, checked_in_by):
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
    def ph_number(self):
        return self.request_body["ph_number"]

    @property
    def purpose(self):
        return self.request_body["purpose"]

    @property
    def visit_type(self):
        return self.request_body["visit_type"]

    @property
    def to_meet(self):
        return self.request_body["to_meet"]

    @property
    def card_id(self):
        return self.request_body["card_id"]

    @property
    def comments(self):
        return self.request_body["comments"]

    def to_object(self):
        return {
            "PK": f"visit#{self.current_quarter}",
            "SK": f"visit#{self.visitor_id}#{self.current_time}",
            "name": self.name.lower(),
            "organization": self.organization.lower(),
            "ph_number": self.ph_number,
            "purpose": self.purpose,
            "checked_in_by": self.checked_in_by.lower(),
            "visit_type": self.visit_type,
            "check_in_time": str(self.current_time),
            "to_meet": self.to_meet.lower(),
            "card_id": self.card_id,
            "comments": self.comments.lower() if self.comments else None,
        }