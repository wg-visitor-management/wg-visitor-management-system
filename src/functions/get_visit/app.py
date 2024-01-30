import json
from vms_layer.helpers.rbac import rbac


@rbac
def lambda_handler(event, context):

    return {"statusCode": 200, "body": json.dumps({"success": True})}
