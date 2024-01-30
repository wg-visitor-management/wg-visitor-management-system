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
from vms_layer.utils.loggers import get_logger

logger = get_logger("POST_/visitor")
db_helper = DBHelper(os.environ["DynamoDBTableName"])
bucket_name = os.environ["BucketName"]




@validate_schema(schema=visitor_schema)
@rbac
@handle_errors
def lambda_handler(event, context):
    logger.debug(event)

    epoch_current = current_time_epoch()
    request_body = json.loads(event["body"])
    visitor_id = f"detail#{request_body['firstName']}{request_body['lastName']}#{epoch_current}"
    picture_name_self = visitor_id+"#photo_self"
    picture_name_id = visitor_id+"#photo_id"

    upload_mime_image_binary_to_s3(
        bucket_name,
        picture_name_self,
        request_body["vistorPhotoBlob"],
    )
    upload_mime_image_binary_to_s3(
        bucket_name,
        picture_name_id,
        request_body["idPhotoBlob"],
    )
    
    body = parse_request_body_to_object(request_body, visitor_id, picture_name_self, picture_name_id)

    profilePictureUrl = generate_presigned_url(bucket_name, picture_name_self)
    idProofPictureUrl = generate_presigned_url(bucket_name, picture_name_id)
    db_helper.create_item(body)

    return ParseResponse({"visitorId" : visitor_id, "profilePictureUrl": profilePictureUrl, "idProofPictureUrl": idProofPictureUrl}, 201).return_response()
