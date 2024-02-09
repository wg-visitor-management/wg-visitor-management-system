from vms_layer.utils.date_time_parser import epoch_to_date
from vms_layer.utils.base64_parser import convert_to_base64

class BodyParser:
    """
    This class is used to parse the response body
    """
    def __init__(self, response):
        self.response = response

    def parse_response(self):
        """
        This function is used to parse the response body
        """
        for item in self.response:
            item.pop("PK")
            visitor_id = item["SK"].split("#")[2]
            timestamp = item["SK"].split("#")[1]
            item["visitId"] = convert_to_base64(f"{visitor_id}#{timestamp}") + "=="
            item.pop("SK")
            item["date"] = epoch_to_date(int(item["checkInTime"])).split("T")[0]
            item["checkInTime"] = epoch_to_date(int(item["checkInTime"])).split("T")[1]
            if item.get("checkOutTime"):
                item["checkOutTime"] = epoch_to_date(int(item["checkOutTime"]))
            if item.get("approvalTime"):
                item["approvalTime"] = epoch_to_date(int(item["approvalTime"]))
        return self.response
