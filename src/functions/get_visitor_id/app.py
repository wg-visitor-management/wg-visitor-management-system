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
db_helper = DBHelper(os.getenv("DynamoDBTableName"))
bucket_name = os.getenv("BucketName")


@handle_errors
@rbac
def lambda_handler(event, context):
    logger.debug(event)
    pathParams = event.get("pathParameters", {})
    if not pathParams or "id" not in pathParams:
        raise ValueError("Missing 'id' key in Path Parameters.")
    visitor_id = pathParams.get("id")
    raw_visitor_id = base64_to_string(visitor_id)

    visitor_id = "detail#" + raw_visitor_id
    visitor = db_helper.get_item({"PK": "visitor", "SK": visitor_id})
    if not visitor:
        raise VisitorNotFoundException("Visitor Not Found.")
    profilePictureIdentifier = visitor.get("profilePictureUrl")
    idProofPictureIdentifier = visitor.get("idProofPictureUrl")
    profilePictureUrl = None
    idProofPictureUrl = None
    if profilePictureIdentifier and idProofPictureIdentifier:
        profilePictureUrl = generate_presigned_url(
            bucket_name, profilePictureIdentifier
        )
        idProofPictureUrl = generate_presigned_url(
            bucket_name, idProofPictureIdentifier
        )
    visitor.pop("PK")
    visitor.pop("SK")
    visitor_id = convert_to_base64(visitor_id.split("#")[-1])
    return ParseResponse(
        {
            **visitor,
            "visitorId": visitor_id,
            "profilePictureUrl": profilePictureUrl,
            "idProofPictureUrl": idProofPictureUrl,
        },
        200,
    ).return_response()
