from functools import wraps
import json
from jsonschema import validate, ValidationError

from vms_layer.helpers.response_parser import ParseResponse


def validate_schema(schema):
    """Validates the schema of the request body."""

    def decorator(func):
        @wraps(func)
        def wrapper(event, context):
            try:
                validate(json.loads(event.get("body")), schema)
            except ValidationError as e:
                return ParseResponse(e.message, 400).return_response()
            return func(event, context)

        return wrapper

    return decorator
