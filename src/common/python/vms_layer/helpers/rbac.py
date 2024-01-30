from vms_layer.config.config import RBAC_CONFIG
from vms_layer.helpers.response_parser import ParseResponse
def rbac(func):
    def wrapper(event, context):
        group = (
            event.get("requestContext")
            .get("authorizer")
            .get("claims")
            .get("cognito:groups")
        )
        if group:
            http_method = event.get("httpMethod")
            resource = event.get("resource")
            allowed_methods = RBAC_CONFIG.get(group)
            allowed_methods = allowed_methods.get(resource)
            if allowed_methods and http_method in allowed_methods:
                return func(event, context)

        return ParseResponse({"message": "Access Denied"}, 403).return_response()

    return wrapper
