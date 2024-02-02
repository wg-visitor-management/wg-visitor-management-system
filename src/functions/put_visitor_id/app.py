from datetime import datetime
import os
import json

from helpers.body_parser import parse_request_body_to_object
from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.utils.base64_parser import base64_to_string
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.config.schemas.visitor_schema import visitor_schema
from vms_layer.utils.date_time_parser import current_time_epoch
from vms_layer.utils.s3_signed_url_generator import generate_presigned_url

logger = get_logger("GET_/visitor/:id")
db_helper = DBHelper(os.environ["DynamoDBTableName"])
bucket_name = os.environ["BucketName"]

@handle_errors
@rbac
@validate_schema(schema=visitor_schema)
def lambda_handler(event, context):
    logger.debug(event)
    
    request_body = json.loads(event.get("body"))

    visitor_id = event["pathParameters"]["id"]
    raw_visitor_id = base64_to_string(visitor_id)

    old_first_name = request_body.get("oldFirstName").replace(" ", "").lower()
    old_last_name = request_body.get("oldLastName").replace(" ", "").lower()
    visitor_id = f"detail#{old_first_name}{old_last_name}#{raw_visitor_id}"
    visitor_history_id = f"detail#{raw_visitor_id}"
    picture_name_self = f"{raw_visitor_id}#photo_self"
    picture_name_id = f"{raw_visitor_id}#photo_id"

    vistor_pk_body = parse_request_body_to_object(
        request_body, picture_name_self, picture_name_id)

    updated_data = update_visitor_data(vistor_pk_body, visitor_id, raw_visitor_id)

    delete_old_visitor_data(visitor_id)

    update_visitor_history(vistor_pk_body, visitor_history_id)

    update_picture_urls(updated_data, bucket_name, picture_name_self, picture_name_id)

    return ParseResponse(updated_data.get("Attributes"), 200).return_response()

def update_visitor_data(visitor_data, visitor_id, raw_visitor_id):
    updated_visitor_id = f"detail#{visitor_data['firstName']}{visitor_data['lastName']}#{raw_visitor_id}"
    visitor_data.update({"PK": "visitor", "SK": visitor_id})
    
    return db_helper.update_item(
        {"PK": "visitor", "SK": updated_visitor_id},
        "SET firstName = :firstName, lastName = :lastName, phoneNumber = :phoneNumber, email = :email, organisation = :organisation, address = :address, idProofNumber = :idProofNumber",
        {
            ":firstName": visitor_data["firstName"],
            ":lastName": visitor_data["lastName"],
            ":phoneNumber": visitor_data["phoneNumber"],
            ":email": visitor_data["email"],
            ":organisation": visitor_data["organisation"],
            ":address": visitor_data["address"],
            ":idProofNumber": visitor_data["idProofNumber"],
        }
    )

def delete_old_visitor_data(visitor_id):
    db_helper.delete_item({"PK": "visitor", "SK": visitor_id})

def update_visitor_history(visitor_data, visitor_history_id):
    current_year = datetime.now().year
    epoch_current = current_time_epoch()

    history_pk_body = visitor_data.copy()
    history_pk_body.update({
        "PK": f"detail_history#{current_year}",
        "SK": f"{visitor_history_id}#{epoch_current}"
    })

    db_helper.create_item(history_pk_body)

def update_picture_urls(updated_data, bucket_name, picture_name_self, picture_name_id):
    profile_picture_url = generate_presigned_url(bucket_name, picture_name_self)
    id_proof_picture_url = generate_presigned_url(bucket_name, picture_name_id)
    updated_data["Attributes"]["profilePictureUrl"] = profile_picture_url
    updated_data["Attributes"]["idProofPictureUrl"] = id_proof_picture_url
