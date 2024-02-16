"""
This module is responsible for updating the 
check out time for the visit and history partition
"""
import base64

from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.utils.date_time_parser import epoch_to_date
from vms_layer.utils.date_time_parser import extract_quarters_from_date_range
from vms_layer.utils.date_time_parser import current_time_epoch
from vms_layer.helpers.rbac import rbac
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.loggers import get_logger

logger = get_logger("PATCH /visit/:id")



@handle_errors
@rbac
def lambda_handler(event, context):
    """
    Update the check out time for the visit and history partition
    """
    logger.debug("Received event: %s", event)
    logger.debug("Received context: %s", context)
    visit_id = event.get("pathParameters").get("id")
    db_helper = DBHelper()
    decoded_visit_id = base64.b64decode(visit_id).decode("utf-8")
    visitor_id = decoded_visit_id.split("#")[0]
    timestamp = decoded_visit_id.split("#")[1]
    current_time = current_time_epoch()

    quarter = extract_quarters_from_date_range(
        epoch_to_date(int(timestamp)), epoch_to_date(int(timestamp))
    )[0]

    response_visit = db_helper.update_item(
        key={"PK": f"visit#{quarter}", "SK": f"visit#{visitor_id}#{timestamp}"},
        update_expression="SET checkOutTime = :checkOutTime",
        expression_attribute_values={":checkOutTime": str(current_time)},
    )
    response_history = db_helper.update_item(
        key={"PK": f"history#{quarter}", "SK": f"history#{timestamp}#{visitor_id}"},
        update_expression="SET checkOutTime = :checkOutTime",
        expression_attribute_values={":checkOutTime": str(current_time)},
    )
    logger.debug("Response from update_item: %s", response_visit)
    logger.debug("Response from update_item: %s", response_history)

    logger.info("Visit checked out successfully")
    return ParseResponse(
        {
            "message": "Visit checked out successfully",
        },
        200,
    ).return_response()
