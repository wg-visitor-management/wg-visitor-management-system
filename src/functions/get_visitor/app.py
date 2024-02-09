import json
import os

from vms_layer.utils.base64_parser import convert_to_base64, base64_to_string
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.config.config import CARD_STATUS
from vms_layer.helpers.response_parser import ParseResponse
 
db_helper = DBHelper(os.getenv("DynamoDBTableName"))
logger = get_logger("GET /visitor")

def lambda_handler(event, context):
    logger.debug("Received event: %s", event)
    query_params = event.get("queryStringParameters")
    search_key = query_params.get("name", "").lower()
    last_evaluated_key = query_params.get("nextPageToken")
    organization = query_params.get("organization")
    page_size = int(query_params.get("maxItems", 10))

    filter_expression = generate_filter_expression(organization)
    expression_attribute_values = generate_expression_attribute_values(organization)
    
    return get_visitor_by_name(search_key, filter_expression, expression_attribute_values, last_evaluated_key, page_size)

def get_visitor_by_name(search_key, filter_expression, expression_attribute_values, last_evaluated_key, page_size):
    logger.debug("Getting visitor by name: %s", search_key)
    if last_evaluated_key:
        last_evaluated_key = json.loads(base64_to_string(last_evaluated_key))
    
    expression_attributes = {":pk": "visitor", ":sk": f"detail#{search_key}"}
    if expression_attribute_values:
        expression_attributes.update(expression_attribute_values)
    
    data, next_page_token = query_items(
        key_condition_expression="PK = :pk AND begins_with(SK, :sk)",
        expression_attribute_values= expression_attributes,
        filter_expression=filter_expression,
        starting_token=last_evaluated_key,
        page_size=page_size
    )
    return format_response(data, next_page_token)

def format_response(data, next_page_token):
    logger.debug("Formatting response")
    if data:
        for item in data:
            item['visitor_id'] = convert_to_base64(item.get('SK').split('#')[-1])
            item.pop("PK")
            item.pop("SK")
        response = {
            "visitors": data,
            "nextPageToken": next_page_token,
        }
        return ParseResponse(response, 200).return_response()
    return ParseResponse([], 200).return_response()

def query_items(
    key_condition_expression,
    starting_token,
    page_size,
    filter_expression=None,
    expression_attribute_values=None
):
    logger.debug("Querying items")
    if not expression_attribute_values:
        expression_attribute_values = {}
    if not filter_expression:
        filter_expression = ""
    if not starting_token:
        starting_token = {}
    response = db_helper.query_items(
        key_condition_expression=key_condition_expression,
        expression_attribute_values=expression_attribute_values,
        page_size=page_size,
        starting_token=starting_token,
        filter_expression=filter_expression,
    )
    items = response.get("Items")
    last_evaluated_key = None
    if response.get("LastEvaluatedKey"):
        last_evaluated_key = response.get("LastEvaluatedKey")
        last_evaluated_key = json.dumps(last_evaluated_key)
        last_evaluated_key = convert_to_base64(last_evaluated_key)
    
    logger.debug(f"Items Q: {items}")
    return items, last_evaluated_key

def generate_filter_expression(organization):
    logger.debug("Generating filter expression for organization: %s", organization)
    return f"contains(organization, :organization)" if organization else ""

def generate_expression_attribute_values(organization):
    logger.debug("Generating expression attribute values for organization: %s", organization)
    return {":organization": organization} if organization else {}