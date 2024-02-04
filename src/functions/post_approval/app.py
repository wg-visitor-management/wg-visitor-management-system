import json
import os
import boto3
import jwt
from datetime import datetime, timedelta
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.utils.base64_parser import base64_to_string
from vms_layer.utils.loggers import get_logger
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.date_time_parser import (
    extract_quarters_from_date_range,
    epoch_to_date,
    current_time_epoch,
)
from vms_layer.config.schemas.approval_schema import post_approval_schema

client = boto3.client("ses")
logger = get_logger("POST /approval")
db_helper = DBHelper(os.getenv("DynamoDBTableName"))


@handle_errors
@rbac
@validate_schema(post_approval_schema)
def lambda_handler(event, context):
    body = json.loads(event.get("body"))

    visit_id = body.get("visitId")
    dt = datetime.utcnow() + timedelta(hours=1)
    name = body.get("name")
    access_token = jwt.encode({"name": name, "exp": dt}, os.getenv("JWT_SECRET"))
    organization = body.get("organization")
    ph_number = body.get("phNumber")
    purpose = body.get("purpose")
    decoded_visit_id = base64_to_string(visit_id)
    visitor_id, timestamp = decoded_visit_id.split("#")
    current_time = current_time_epoch()
    current_quarter = extract_quarters_from_date_range(
        epoch_to_date(current_time), epoch_to_date(current_time)
    )[0]

    update_database_items(current_quarter, decoded_visit_id, visitor_id, timestamp)

    send_email(
        "vms_email_template-test",
        os.getenv("SENDER_EMAIL"),
        os.getenv("RECIPIENT_EMAIL"),
        "A visitor needs your approval for entry!",
        json.dumps(
            {
                "name": name,
                "organization": organization,
                "ph_number": ph_number,
                "purpose": purpose,
                "access_token": access_token,
                "visit_id": visit_id,
            }
        ),
    )
    logger.info("Approval request sent successfully")
    return ParseResponse(
        {"message": "Approval request sent successfully"}, 200
    ).return_response()


def update_database_items(current_quarter, decoded_visit_id, visitor_id, timestamp):
    logger.info(f"Updating visit {decoded_visit_id} with approval status")
    db_helper.update_item(
        key={"PK": f"visit#{current_quarter}", "SK": f"visit#{decoded_visit_id}"},
        update_expression="SET approvalStatus = :approved",
        expression_attribute_values={":approved": "pending"},
    )

    db_helper.update_item(
        key={
            "PK": f"history#{current_quarter}",
            "SK": f"history#{timestamp}#{visitor_id}",
        },
        update_expression="SET approvalStatus = :approved",
        expression_attribute_values={":approved": "pending"},
    )


def send_email(template_name, sender, recipient, subject, body):
    logger.info(f"Sending email to {recipient}")
    response = client.send_templated_email(
        Source=sender,
        Destination={"ToAddresses": [recipient]},
        Template=template_name,
        TemplateData=body,
    )

    logger.debug(f"Email sent successfully: {response}")
