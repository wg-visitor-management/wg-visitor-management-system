import os
import json
from datetime import datetime

from helpers.body_parser import Body
from vms_layer.helpers.s3_helpers import upload_mime_image_binary_to_s3
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

logger = get_logger("POST /visitor")
db_helper = DBHelper(os.getenv("DynamoDBTableName"))
bucket_name = os.getenv("BucketName")


@handle_errors
@rbac
@validate_schema(schema=visitor_schema)
def lambda_handler(event, context):
    logger.debug(event)
    current_year = datetime.now().year
    epoch_current = current_time_epoch()
    request_body = json.loads(event.get("body"))
    first_name = request_body.get("firstName").replace(" ", "").lower()
    last_name = request_body.get("lastName").replace(" ", "").lower()
    raw_visitor_id = f"{epoch_current}"
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

    body = Body(request_body, picture_name_self, picture_name_id)

    visitor_body = body.to_object()
    history_body = visitor_body.copy()

    visitor_body["PK"] = "visitor"
    visitor_body["SK"] = f"detail#{first_name}{last_name}#{raw_visitor_id}"
    db_helper.create_item(visitor_body)

    history_body["PK"] = f"detail_history#{current_year}"
    history_body["SK"] = f"{visitor_id}#{epoch_current}"
    db_helper.create_item(history_body)

    profile_picture_url = generate_presigned_url(bucket_name, picture_name_self)
    id_proof_picture_url = generate_presigned_url(bucket_name, picture_name_id)
    return ParseResponse(
        {
            "visitorId": str(encoded_visitor_id),
            "profilePictureUrl": profile_picture_url,
            "idProofPictureUrl": id_proof_picture_url,
        },
        201,
    ).return_response()
