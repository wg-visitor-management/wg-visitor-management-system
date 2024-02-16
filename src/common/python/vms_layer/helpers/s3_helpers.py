import base64
import boto3

from vms_layer.utils.loggers import get_logger
from vms_layer.utils.custom_errors import FailedToUploadImageError

logger = get_logger(__name__)
s3 = boto3.client("s3")


def upload_mime_image_binary_to_s3(
    bucket_name, file_name, binary_data, content_type="image/jpg"
):
    """Uploads a base64 encoded image to S3 bucket"""
    try:
        response = s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=base64.b64decode(binary_data.encode() + b"=="),
            ContentType=content_type,
        )
    except Exception as error:
        raise FailedToUploadImageError(
            error.message if hasattr(error, "message") else str(error)
        )
    return True
