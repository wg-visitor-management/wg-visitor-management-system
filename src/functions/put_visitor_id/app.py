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
from vms_layer.utils.custom_errors import VisitorNotFoundException


logger = get_logger("PUT /visitor/:id")
db_helper = DBHelper()
bucket_name = os.getenv("BucketName")


@handle_errors
@rbac
@validate_schema(schema=visitor_schema)
def lambda_handler(event, context):
    logger.debug(event)

    request_body = json.loads(event.get("body"))

    visitor_id = event["pathParameters"]["id"]
    raw_visitor_id = base64_to_string(visitor_id)

    old_first_name = string_trim_lower(request_body.get("oldFirstName"))
    old_last_name = string_trim_lower(request_body.get("oldLastName"))
    visitor_id = f"detail#{old_first_name}{old_last_name}#{raw_visitor_id}"

    visitor_details = db_helper.get_item({"PK": "visitor", "SK": visitor_id})
    if not visitor_details:
        raise VisitorNotFoundException("Visitor Not Found.")

    visitor_history_id = f"detail#{raw_visitor_id}"
    picture_name_self = visitor_details.get("profilePictureUrl")
    picture_name_id = visitor_details.get("idProofPictureUrl")


    vistor_pk_body = parse_request_body_to_object(
        request_body, picture_name_self, picture_name_id
    )

    updated_data = update_visitor_data(vistor_pk_body, visitor_id, raw_visitor_id)

    delete_old_visitor_data(visitor_id)

    update_visitor_history(vistor_pk_body, visitor_history_id)

    update_picture_urls(updated_data, bucket_name, picture_name_self, picture_name_id)

    return ParseResponse(updated_data.get("Attributes"), 200).return_response()


def update_visitor_data(visitor_data, visitor_id, raw_visitor_id):
    updated_visitor_id = f"detail#{string_trim_lower(visitor_data['firstName'])}{string_trim_lower(visitor_data['lastName'])}#{raw_visitor_id}"
    visitor_data.update({"PK": "visitor", "SK": visitor_id})

    return db_helper.update_item(
        {"PK": "visitor", "SK": updated_visitor_id},
        "SET firstName = :firstName, lastName = :lastName, phoneNumber = :phoneNumber, email = :email, organization = :organization, address = :address, idProofNumber = :idProofNumber, profilePictureUrl = :profilePictureUrl, idProofPictureUrl = :idProofPictureUrl",
        {
            ":firstName": visitor_data["firstName"],
            ":lastName": visitor_data["lastName"],
            ":phoneNumber": visitor_data["phoneNumber"],
            ":email": visitor_data["email"],
            ":organization": visitor_data["organization"],
            ":address": visitor_data["address"],
            ":idProofNumber": visitor_data["idProofNumber"],
            ":profilePictureUrl": visitor_data["profilePictureUrl"],
            ":idProofPictureUrl": visitor_data["idProofPictureUrl"],
        },
    )


def delete_old_visitor_data(visitor_id):
    db_helper.delete_item({"PK": "visitor", "SK": visitor_id})


def update_visitor_history(visitor_data, visitor_history_id):
    current_year = datetime.now().year
    epoch_current = current_time_epoch()

    history_pk_body = visitor_data.copy()
    history_pk_body.update(
        {
            "PK": f"detail_history#{current_year}",
            "SK": f"{visitor_history_id}#{epoch_current}",
        }
    )

    db_helper.create_item(history_pk_body)


def update_picture_urls(updated_data, bucket_name, picture_name_self, picture_name_id):
    profile_picture_url = generate_presigned_url(bucket_name, picture_name_self)
    id_proof_picture_url = generate_presigned_url(bucket_name, picture_name_id)
    updated_data["Attributes"]["profilePictureUrl"] = profile_picture_url
    updated_data["Attributes"]["idProofPictureUrl"] = id_proof_picture_url


def string_trim_lower(_string):
    return _string.replace(" ", "").lower()
