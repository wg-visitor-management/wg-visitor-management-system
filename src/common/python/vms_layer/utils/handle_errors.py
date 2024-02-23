import os
import functools
import traceback

from vms_layer.utils.loggers import get_logger
from vms_layer.helpers.response_parser import ParseResponse
from vms_layer.config.config import error_map
APP_NAME = os.getenv("ApplicationName")

logger = get_logger(APP_NAME)

def handle_errors(function):
    """Decorator to handle errors"""
    
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return_value = function(*args, **kwargs)
            return return_value
        except Exception as error:
            return get_error_response(error)
    return wrapper

def get_error_response(error):
    """Identify the error"""

    if type(error) in error_map:
        status_code = error_map.get(type(error))
    else:
        status_code = error_map.get(Exception)
    logger.error(
                f"Error Occurred: {traceback.format_exc()}"
            )
    return ParseResponse(
        error.message if hasattr(error, "message") else str(error),
        status_code).return_response()
    


def error_parser(error):
    """To Parse the error message in json schema validator"""
    try:
        message = error.schema.get("message").get(error.validator)
        return message
    except Exception as e:
        return error.message.split("\n")[0]