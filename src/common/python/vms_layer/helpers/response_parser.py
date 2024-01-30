import json


class ParseResponse:
    def __init__(self, response, status_code):
        self.response = response
        self.status_code = status_code
        self.status = self.evaluate_status()

    def return_response(self):
        response = {
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": True,
                "Content-Type": "application/json",
                "X-Requested-With": "*",
            },
            "statusCode": self.status_code,
            "body": json.dumps(self.parse_body()),
        }
        return response

    def parse_body(self):
        if self.status == "success":
            return {
                "status": self.status,
                "data": self.response,
            }
        else:
            return {
                "status": self.status,
                "error": {"message": self.response, "code": self.status_code},
            }

    def evaluate_status(self):
        if self.status_code >= 200 and self.status_code <= 399:
            status = "success"
        else:
            status = "failure"
        return status
