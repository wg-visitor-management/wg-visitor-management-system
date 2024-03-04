"""
This module contains the code for the get_visitor_id lambda function.
"""

import os
from datetime import datetime
from vms_layer.utils.custom_errors import VisitorNotFoundException
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.helpers.response_parser import ParseResponse, remove_keys
from vms_layer.utils.s3_signed_url_generator import generate_presigned_url
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.utils.base64_parser import base64_to_string, convert_to_base64


APP_NAME = os.getenv("ApplicationName")
BUCKET_NAME = os.getenv("BucketName")

logger = get_logger(APP_NAME)
db_helper = DBHelper()


@handle_errors
@rbac
def lambda_handler(event, context):
    """
    This function is used to get a visitor from the database.
    """
    logger.debug(f"Received event: {event}")
    logger.debug(f"Received context: {context}")

    visitor_id = extract_visitor_id(event)
    visitor = get_visitor_from_database(visitor_id)
    profile_picture_url, id_proof_picture_url = get_picture_urls(visitor)

    visitor = remove_keys(visitor, ["PK", "SK"])
    visitor_id = convert_to_base64(visitor_id.split("#")[-1])

    return ParseResponse(
        {
            **visitor,
            "visitorId": visitor_id,
            "profilePictureUrl": profile_picture_url,
            "idProofPictureUrl": id_proof_picture_url,
        },
        200,
    ).return_response()


def extract_visitor_id(event):
    """
    Extracts the visitor ID from the event path parameters.
    """
    path_params = event.get("pathParameters", {})
    if not path_params or "id" not in path_params:
        raise ValueError("Missing 'id' key in Path Parameters.")
    visitor_id = path_params.get("id")
    return base64_to_string(visitor_id)


def get_visitor_from_database(visitor_id):
    """
    Retrieves the visitor details from the database.
    """
    current_year = datetime.now().year
    response = db_helper.query_items(
        key_condition_expression="PK = :pk AND begins_with(SK, :sk)",
        expression_attribute_values={
            ":pk": f"detail_history#{current_year}",
            ":sk": f"detail#{visitor_id}",
        },
        consistent_read=True
    )
    latest_visitor_details = response.get("Items")[-1]
    first_name = latest_visitor_details.get("firstName").replace(" ", "").lower()
    last_name = latest_visitor_details.get("lastName").replace(" ", "").lower()
    visitor_name = f"{first_name}{last_name}"
    visitor_id = "detail#" + visitor_name + "#" + visitor_id
    visitor = db_helper.get_item({"PK": "visitor", "SK": visitor_id})
    if not visitor:
        raise VisitorNotFoundException("Visitor Not Found.")
    return visitor


def get_picture_urls(visitor):
    """
    Generates the pre-signed URLs for the visitor's profile picture and ID proof picture.
    """
    profile_picture_identifier = visitor.get("profilePictureUrl")
    id_proof_picture_identifier = visitor.get("idProofPictureUrl")
    profile_picture_url = None
    id_proof_picture_url = None
    if profile_picture_identifier and id_proof_picture_identifier:
        profile_picture_url = generate_presigned_url(
            BUCKET_NAME, profile_picture_identifier
        )
        id_proof_picture_url = generate_presigned_url(
            BUCKET_NAME, id_proof_picture_identifier
        )
    return profile_picture_url, id_proof_picture_url
