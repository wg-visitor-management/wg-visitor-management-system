import os

from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.utils.custom_errors import InvalidCardIdError

db_helper = DBHelper(os.getenv("DynamoDBTableName"))
logger = get_logger("POST_/card")


@handle_errors
@rbac
def lambda_handler(event, context):
    card_id = event.get('pathParameters').get('id')

    data = db_helper.get_item({"PK": "card", "SK": f"card#{card_id}"})
    if data:
        data.pop("PK")
        data['card_id'] = data.get('SK').split("#")[-1]
        data.pop("SK")
        return ParseResponse(data, 200).return_response()
    
    raise InvalidCardIdError("Invalid Card Id Provided")
