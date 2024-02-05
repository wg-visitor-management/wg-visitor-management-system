import json
import os
import base64
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.utils.date_time_parser import epoch_to_date
from vms_layer.utils.date_time_parser import extract_quarters_from_date_range
from vms_layer.utils.date_time_parser import current_time_epoch
from vms_layer.helpers.rbac import rbac
from vms_layer.utils.handle_errors import handle_errors


from vms_layer.helpers.db_helper import DBHelper

@handle_errors
@rbac
def lambda_handler(event, context):
    visit_id = event.get("pathParameters").get("id")

    db_helper = DBHelper(os.environ.get("DynamoDBTableName"))

    decoded_visit_id = base64.b64decode(visit_id).decode("utf-8")

    visitor_id = decoded_visit_id.split("#")[0]
    timestamp = decoded_visit_id.split("#")[1]
    current_time = current_time_epoch()

    quarter = extract_quarters_from_date_range(
        epoch_to_date(int(timestamp)), epoch_to_date(int(timestamp))
    )[0]

    response = db_helper.update_item(
        key={"PK": f"visit#{quarter}", "SK": f"visit#{visitor_id}#{timestamp}"},
        update_expression="SET checkOutTime = :checkOutTime",
        expression_attribute_values={":checkOutTime": str(current_time)},
    )

    response = db_helper.update_item(
        key={"PK": f"history#{quarter}", "SK": f"history#{timestamp}#{visitor_id}"},
        update_expression="SET checkOutTime = :checkOutTime",
        expression_attribute_values={":checkOutTime": str(current_time)},
    )

    return ParseResponse(
        {
            "message": "Visit checked out successfully",
        },
        200,
    ).return_response()
