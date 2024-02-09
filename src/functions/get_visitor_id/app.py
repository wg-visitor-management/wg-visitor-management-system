"""
This module contains the code for the get_visitor_id lambda function.
"""
import os

from vms_layer.utils.custom_errors import VisitorNotFoundException
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.utils.s3_signed_url_generator import generate_presigned_url
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.utils.base64_parser import base64_to_string, convert_to_base64


logger = get_logger("GET /visitor/:id")
db_helper = DBHelper()
bucket_name = os.getenv("BucketName")


@handle_errors
@rbac
def lambda_handler(event, context):
    """
    This function is used to get a visitor from the database.
    """
    logger.debug(event)
    logger.debug("Received context: %s", context)

    path_params = event.get("pathParameters", {})
    if not path_params or "id" not in path_params:
        raise ValueError("Missing 'id' key in Path Parameters.")
    visitor_id = path_params.get("id")
    raw_visitor_id = base64_to_string(visitor_id)

    visitor_id = "detail#" + raw_visitor_id
    visitor = db_helper.get_item({"PK": "visitor", "SK": visitor_id})
    if not visitor:
        raise VisitorNotFoundException("Visitor Not Found.")
    profile_picture_identifier = visitor.get("profilePictureUrl")
    id_proof_picture_identifier = visitor.get("idProofPictureUrl")
    profile_picture_url = None
    id_proof_picture_url = None
    if profile_picture_identifier and id_proof_picture_identifier:
        profile_picture_url = generate_presigned_url(
            bucket_name, profile_picture_identifier
        )
        id_proof_picture_url = generate_presigned_url(
            bucket_name, id_proof_picture_identifier
        )
    visitor.pop("PK")
    visitor.pop("SK")
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
