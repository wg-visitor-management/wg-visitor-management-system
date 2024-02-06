import os
from vms_layer.utils.base64_parser import convert_to_base64
 
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.config.config import CARD_STATUS
from vms_layer.helpers.response_parser import ParseResponse
 
db_helper = DBHelper(os.getenv("DynamoDBTableName"))
logger = get_logger("GET /visitor")
 
 
@handle_errors
@rbac
def lambda_handler(event, context):
    search_key = ""
    query_params = event.get("queryStringParameters")
    if query_params:
        search_key = query_params.get("name")
        if search_key:
            search_key = search_key.lower()
    return get_visitor_by_name(search_key)
 
 
def get_visitor_by_name(search_key):
    data = query_items(db_helper,
        key_condition_expression="PK = :pk AND begins_with(SK, :sk)",
        expression_attribute_values={":pk": "visitor", ":sk": f"detail#{search_key}"}
    )
    if data:
        for item in data:
            item['visitor_id'] = convert_to_base64(item.get('SK').split('#')[-1])
            item.pop("PK")
            item.pop("SK")
 
        return ParseResponse(data, 200).return_response()
    return ParseResponse([], 200).return_response()

def query_items(
    db_helper,
    key_condition_expression,
    filter_expression=None,
    expression_attribute_values=None,
):
    """Query items from the table"""
    items = []
    response = db_helper.query_items(
        key_condition_expression=key_condition_expression,
        page_size=int(10),
        filter_expression=filter_expression,
        expression_attribute_values=expression_attribute_values,
    )
    items += response["Items"]
    logger.debug(f"Items: {items}")
    while "LastEvaluatedKey" in response:
        response = db_helper.query_items(
            key_condition_expression=key_condition_expression,
            page_size=int(10),
            starting_token=response["LastEvaluatedKey"],
            filter_expression=filter_expression,
            expression_attribute_values=expression_attribute_values,
        )
        items += response["Items"]

    logger.debug(f"Items Q: {items}")
    return items