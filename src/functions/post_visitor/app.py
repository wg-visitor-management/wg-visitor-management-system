import json
import os
import boto3


from vms_layer.helpers.rbac import rbac
from vms_layer.helpers.validate_schema import validate_schema
from vms_layer.config.schemas.visitor_schema import visitor_schema
from vms_layer.helpers.db_helper import DBHelper
from vms_layer.utils.date_time_parser import current_time_epoch
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.utils.s3_signed_url_generator import generate_presigned_url

db_helper = DBHelper(os.environ["DynamoDBTableName"])
bucket_name = os.environ["BucketName"]
bucket_name = "vms-static-content"
s3 = boto3.client("s3")


def upload_mime_image_binary_to_s3(
    bucket_name, file_name, binary_data, content_type="image/png"
):
    try:
        response = s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=binary_data,
            ContentType=content_type,
        )
        print(response)
    except Exception as error:
        print(error)
        return False
    return True

@validate_schema(schema=visitor_schema)
@rbac
def lambda_handler(event, context):
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
    body = {}
    
    body["PK"] = "visitor"
    body["SK"] = visitor_id
    body["firstName"] = request_body["firstName"]
    body["lastName"] = request_body["lastName"]
    body["phoneNumber"] = request_body["phoneNumber"]
    body["email"] = request_body["email"]
    body["organisation"] = request_body["organisation"]
    body["address"] = request_body["address"]
    body["idProofNumber"] = request_body["idProofNumber"]
    body["profilePictureUrl"] = picture_name_self
    body["idProofPictureUrl"] = picture_name_id

    profilePictureUrl = generate_presigned_url(bucket_name, picture_name_self)
    idProofPictureUrl = generate_presigned_url(bucket_name, picture_name_id)
    db_helper.create_item(body)

    return ParseResponse({"visitorId" : visitor_id, "profilePictureUrl": profilePictureUrl, "idProofPictureUrl": idProofPictureUrl}, 201).return_response()
