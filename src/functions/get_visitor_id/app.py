import os

from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.utils.s3_signed_url_generator import generate_presigned_url
from vms_layer.utils.handle_errors import handle_errors
from vms_layer.utils.loggers import get_logger
from vms_layer.utils.base64_parser import base64_to_string


logger = get_logger("GET_/visitor/:id")
db_helper = DBHelper(os.environ["DynamoDBTableName"])
bucket_name = os.environ["BucketName"]

@handle_errors
@rbac
def lambda_handler(event, context):
    logger.debug(event)
    visitor_id = event["pathParameters"]["id"]
    raw_visitor_id = base64_to_string(visitor_id)
    visitor_id = "detail#" + raw_visitor_id
    visitor = db_helper.get_item({"PK": "visitor", "SK": visitor_id})
    
    profilePictureUrl = generate_presigned_url(bucket_name, visitor["profilePictureUrl"])
    idProofPictureUrl = generate_presigned_url(bucket_name, visitor["idProofPictureUrl"])
    return ParseResponse({**visitor, "profilePictureUrl": profilePictureUrl, "idProofPictureUrl": idProofPictureUrl}, 200).return_response()