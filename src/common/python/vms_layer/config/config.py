import json
from vms_layer.utils.custom_errors import CardAlreadyExistsError, NotAuthorizedException, UnauthorizedError, ConflictError, AuthenticationError, FailedToUploadImageError, InvalidCardIdError, UserNotFoundException, VisitorNotFoundException
def load_configuration():
    """Load the configuration file and return the parameters"""
   
    with open('/opt/python/vms_layer/config/config.json', "r") as file:
        config = json.load(file)
        rbac_config = config.get("ACCESS_CONTROL_LIST")
        log_config = config.get("LOG_CONFIGURATIONS")
        card_status = config.get("CARD_STATUS")
        return rbac_config, log_config, card_status
 
(RBAC_CONFIG, LOG_CONFIG, CARD_STATUS) = load_configuration()
error_map = {
        UnauthorizedError: 401,
        ConflictError: 409,
        ValueError: 400,
        AuthenticationError: 401,
        FailedToUploadImageError: 500,
        CardAlreadyExistsError : 400,
        InvalidCardIdError : 400,
        NotAuthorizedException : 403,
        UserNotFoundException : 404,
        VisitorNotFoundException : 404,
        Exception : 500
    }