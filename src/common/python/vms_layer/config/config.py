from vms_layer.utils.custom_errors import CardAlreadyExistsError, NotAuthorizedException, UnauthorizedError, ConflictError, AuthenticationError, FailedToUploadImageError, InvalidCardIdError, UserNotFoundException, VisitorNotFoundException

RBAC_CONFIG = {
  "admin": {
    "/card": ["GET", "POST"],
    "/card/{id}": ["GET", "PUT", "DELETE"],
    "/approval": ["GET", "POST"],
    "/approval/{id}": ["GET", "PATCH"],
    "/visitor": ["GET", "POST"],
    "/visitor/{id}": ["GET", "PUT"],
    "/visit": ["GET", "POST"],
    "/visit/{id}": ["GET", "PATCH"]
  },
  "user": {
    "/card": ["GET"],
    "/card/{id}": ["GET", "PUT"],
    "/approval": ["GET", "POST"],
    "/approval/{id}": ["GET"],
    "/visitor": ["GET", "POST"],
    "/visitor/{id}": ["GET", "PUT"],
    "/visit": ["GET", "POST"],
    "/visit/{id}": ["GET", "PATCH"]
  }
}

LOG_CONFIG = {
  "LOG_LEVEL": "DEBUG",
  "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  "LOG_DATE_FORMAT": "%Y-%m-%d %H:%M:%S"
}

CARD_STATUS = {
  "AVAILABLE": "available",
  "OCCUPIED": "occupied",
  "DISCARDED": "discarded"
}

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