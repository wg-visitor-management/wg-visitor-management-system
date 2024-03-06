import os

from vms_layer.utils.custom_errors import UnauthorizedError
from vms_layer.config.config import RBAC_CONFIG
from vms_layer.utils.loggers import get_logger

APP_NAME = os.getenv("ApplicationName")

logger = get_logger(APP_NAME)


def rbac(func):
    """Role Based Access Control Decorator"""

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
        raise UnauthorizedError("Unauthorized Access")

    return wrapper
