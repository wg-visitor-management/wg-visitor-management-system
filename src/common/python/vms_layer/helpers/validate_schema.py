from functools import wraps
import json
from jsonschema import validate, ValidationError


def validate_schema(schema):
    def decorator(func):
        @wraps(func)
        def wrapper(event, context):
            try:
                validate(json.loads(event["body"]), schema)
            except ValidationError as e:
                return {
                    "statusCode": 400,
                    "body": json.dumps(
                        {
                            "error": {"code": 400, "message": e.message},
                            "status": "failure",
                        }
                    ),
                }
            return func(event, context)

        return wrapper

    return decorator
