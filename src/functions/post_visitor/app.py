import base64
import json
import os

from helpers.body_parser import parse_request_body_to_object
from helpers.s3_helpers import upload_mime_image_binary_to_s3
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.config.schemas.visitor_schema import visitor_schema
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.date_time_parser import current_time_epoch
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.utils.s3_signed_url_generator import generate_presigned_url
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.base64_parser import convert_to_base64
from vms_layer.utils.loggers import get_logger
from datetime import datetime

logger = get_logger("POST_/visitor")
db_helper = DBHelper(os.environ["DynamoDBTableName"])
bucket_name = os.environ["BucketName"]


@validate_schema(schema=visitor_schema)
@rbac
@handle_errors
def lambda_handler(event, context):
    logger.debug(event)
    current_year = datetime.now().year
    epoch_current = current_time_epoch()
    request_body = json.loads(event.get("body"))
    first_name = request_body.get("firstName").lower()
    last_name = request_body.get("lastName").replace(" ", "").lower()
    raw_visitor_id = f"{first_name}{last_name}#{epoch_current}"
    encoded_visitor_id = convert_to_base64(raw_visitor_id)

    visitor_id = f"detail#{raw_visitor_id}"
    picture_name_self = f"{raw_visitor_id}#photo_self"
    picture_name_id = f"{raw_visitor_id}#photo_id"

    upload_mime_image_binary_to_s3(
        bucket_name,
        picture_name_self,
        request_body.get("vistorPhotoBlob"),
    )
    upload_mime_image_binary_to_s3(
        bucket_name,
        picture_name_id,
        request_body.get("idPhotoBlob"),
    )

    vistor_pk_body = parse_request_body_to_object(
        request_body, picture_name_self, picture_name_id)
    
    vistor_pk_body["PK"] = "visitor"
    vistor_pk_body["SK"] = visitor_id
    db_helper.create_item(vistor_pk_body)

    history_pk_body = parse_request_body_to_object(
        request_body, picture_name_self, picture_name_id)
    history_pk_body["PK"] = f"detail_history#{current_year}"
    history_pk_body["SK"] = f"detail#{visitor_id}#{epoch_current}"
    db_helper.create_item(history_pk_body)

    profile_picture_url = generate_presigned_url(bucket_name, picture_name_self)
    id_proof_picture_url = generate_presigned_url(bucket_name, picture_name_id)
    return ParseResponse({"visitorId": str(encoded_visitor_id), "profilePictureUrl": profile_picture_url, "idProofPictureUrl": id_proof_picture_url}, 201).return_response()
