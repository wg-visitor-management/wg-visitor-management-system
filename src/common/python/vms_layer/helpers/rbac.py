from vms_layer.config.config import RBAC_CONFIG


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
            allowed_methods = (
                RBAC_CONFIG.get("ACCESS_CONTROL_LIST").get(group).get(resource)
            )
            if allowed_methods and http_method in allowed_methods:
                return func(event, context)

        return {"statusCode": 403, "body": "Access Denied"}

    return wrapper
