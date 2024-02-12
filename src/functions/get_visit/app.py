"""
This module is the entry point for the lambda function
that retrieves visits from the database.
"""
 
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.helpers.rbac import rbac
from visit_helper import VisitHelper
 
logger = get_logger("GET /visit")
 
 
@handle_errors
@rbac
def lambda_handler(event, context):
    """
    This function is used to get all the visits from the database with some filters.
    """
    logger.debug("Received event: %s", event)
    logger.debug("Received context: %s", context)
    query_params = event.get("queryStringParameters")
    start_date = query_params.get("start_date")
    end_date = query_params.get("end_date")
    organization = query_params.get("organization")
    approver = query_params.get("approver")
    visitor_id = query_params.get("visitor_id")
    logger.debug("Query Params: %s", query_params)
    visit_helper = VisitHelper()
    if visitor_id:
        response = visit_helper.get_visits_by_visitor_id(visitor_id)
    elif not (start_date and end_date):
        return ParseResponse(
            {"message": "Please provide start and end date"}, 400
        ).return_response()
    else:
        response = visit_helper.get_filtered_visits_date_range(
            start_date, end_date, organization, approver
        )
 
    return ParseResponse(response, 200).return_response()