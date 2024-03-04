"""This module contains the code for the get_visitor lambda function."""

import os
import json

from vms_layer.utils.base64_parser import convert_to_base64, base64_to_string
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.helpers.response_parser import ParseResponse, remove_keys

APP_NAME = os.getenv("ApplicationName")

logger = get_logger(APP_NAME)
db_helper = DBHelper()

@handle_errors
@rbac
def lambda_handler(event, context):
    """
    This function is used as a handler for the get_visitor lambda function
    """
    logger.debug(f"Received event: {event}")
    logger.debug(f"Received context: {context}")
    query_params = event.get("queryStringParameters")
    search_key = query_params.get("name", "").lower()
    last_evaluated_key = query_params.get("nextPageToken")
    organization = query_params.get("organization")
    page_size = int(query_params.get("maxItems", 10))
    filter_expression = "contains(organization, :organization)" if organization else ""
    expression_attribute_values = (
        {":organization": organization} if organization else {}
    )

    response = get_visitor_by_name(
        search_key,
        filter_expression,
        expression_attribute_values,
        last_evaluated_key,
        page_size,
    )
    logger.info(f"Returning response: {response}")
    return response


def get_visitor_by_name(
    search_key,
    filter_expression,
    expression_attribute_values,
    last_evaluated_key,
    page_size,
):
    """
    This function is used to get the visitor by name
    """
    logger.debug(f"Getting visitor by name: {search_key}")
    if last_evaluated_key:
        last_evaluated_key = json.loads(base64_to_string(last_evaluated_key))

    expression_attributes = {":pk": "visitor", ":sk": f"detail#{search_key}"}
    if expression_attribute_values:
        expression_attributes.update(expression_attribute_values)

    data, next_page_token = query_items(
        key_condition_expression="PK = :pk AND begins_with(SK, :sk)",
        expression_attribute_values=expression_attributes,
        filter_expression=filter_expression,
        starting_token=last_evaluated_key,
        page_size=page_size,
    )
    return format_response(data, next_page_token)


def format_response(data, next_page_token):
    """
    This function is used to format the response
    """
    response = {
        "visitors": [],
        "nextPageToken": None
    }
    
    logger.debug("Formatting response")
    if data:
        for item in data:
            item["visitorId"] = convert_to_base64(item.get("SK").split("#")[-1])
            item = remove_keys(item, ["PK", "SK"])
        response = {
            "visitors": data,
            "nextPageToken": next_page_token,
        }
        return ParseResponse(response, 200).return_response()
    return ParseResponse(response, 200).return_response()


def query_items(
    key_condition_expression,
    starting_token,
    page_size,
    filter_expression=None,
    expression_attribute_values=None,
):
    """
    This function is used to query items from the table
    """
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

    logger.debug(f"Items : {items}")
    return items, last_evaluated_key
