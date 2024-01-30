import boto3
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