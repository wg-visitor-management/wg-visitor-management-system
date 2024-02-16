from functools import wraps
import json
from jsonschema import validate, ValidationError
from vms_layer.utils.handle_errors import error_parser

from vms_layer.helpers.response_parser import ParseResponse


def validate_schema(schema):
    """Validates the schema of the request body."""

    def decorator(func):
        @wraps(func)
        def wrapper(event, context):
            try:
                validate(json.loads(event.get("body")), schema)
            except ValidationError as error:
                validation_resonse = error_parser(error)
                return ParseResponse(validation_resonse, 400).return_response()
            return func(event, context)

        return wrapper

    return decorator
