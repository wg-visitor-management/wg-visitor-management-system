"""
This module is used to send an email to the approver
 and update the visit and history table with the approval status
"""
from datetime import datetime, timedelta
import json
import os
import jwt
import boto3
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

APP_NAME = os.getenv("ApplicationName")

logger = get_logger(APP_NAME)
client = boto3.client("ses")
db_helper = DBHelper()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECIPIENT_EMAIL")
JWT_SECRET = os.getenv("JWT_SECRET")
TEMPLATE_NAME = "vms_email_template-test"


@handle_errors
@rbac
@validate_schema(post_approval_schema)
def lambda_handler(event, context):
    """
    This function is used to send an email to the approver
    and update the visit and history table with the approval status
    """
    body = json.loads(event.get("body"))
    visit_id = body.get("visitId")
    logger.debug(f"Received event: {event}")
    logger.debug(f"Received context: {context}")
    update_visit(visit_id)
    send_email(body)
    logger.info("Approval request sent successfully")
    return ParseResponse(
        {"message": "Approval request sent successfully"}, 200
    ).return_response()


def update_visit(visit_id):
    """
    This function is used to update the visit and history table with the approval status
    """
    logger.debug(f"Updating visit with visit id {visit_id}")
    current_time = current_time_epoch()
    decoded_visit_id = base64_to_string(visit_id)
    visitor_id, timestamp = decoded_visit_id.split("#")
    current_quarter = extract_quarters_from_date_range(
        epoch_to_date(current_time), epoch_to_date(current_time)
    )[0]

    logger.info(f"Updating visit with visit id {decoded_visit_id}")
    visit_response = db_helper.update_item(
        key={"PK": f"visit#{current_quarter}", "SK": f"visit#{decoded_visit_id}"},
        update_expression="SET approvalStatus = :approved",
        expression_attribute_values={":approved": "pending"},
    )
    history_response = db_helper.update_item(
        key={
            "PK": f"history#{current_quarter}",
            "SK": f"history#{timestamp}#{visitor_id}",
        },
        update_expression="SET approvalStatus = :approved",
        expression_attribute_values={":approved": "pending"},
    )
    logger.debug(f"Visit updated successfully: {visit_response}")
    logger.debug(f"History updated successfully: {history_response}")


def send_email(body):
    """
    This function is used to send an email to the approver
    """
    logger.debug(f"Sending email to the approver with body {body}")
    exp_time = datetime.utcnow() + timedelta(seconds=690)
    name = body.get("name")
    visit_id = body.get("visitId")
    organization = body.get("organization")
    ph_number = body.get("phNumber")
    purpose = body.get("purpose")
    for receiver in RECEIVER_EMAIL.split(","):
        logger.debug(f"Sending email to {receiver}")
        access_token = jwt.encode({"name": name, "exp": exp_time, "approver":receiver}, JWT_SECRET)
        email_parameters = json.dumps(
            {
                "name": name,
                "organization": organization,
                "ph_number": ph_number,
                "purpose": purpose,
                "access_token": access_token,
                "visit_id": visit_id,
            }
        )
        logger.info(f"Sending email to {receiver} with parameters {email_parameters}")
        response = client.send_templated_email(
            Source=SENDER_EMAIL,
            Destination={"ToAddresses": [receiver]},
            Template=TEMPLATE_NAME,
            TemplateData=email_parameters,
        )
        logger.info(f"Email sent successfully: {response}")
    return


