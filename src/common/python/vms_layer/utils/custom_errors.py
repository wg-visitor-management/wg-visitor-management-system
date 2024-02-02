
class FailedToUploadImageError(Exception):
    """Failed to upload image to the storage"""
    pass


class UnauthorizedError(Exception):
    """Unauthorized Error"""
    pass

class ConflictError(Exception):
    """Conflict Error"""
    pass

class AuthenticationError(Exception):
    """Authentication Error"""
    pass

class CardAlreadyExistsError(Exception):
    """Card Already Exists Error"""
    pass

class InvalidCardIdError(Exception):
    """Invalid Card Id Error"""
    pass

class NotAuthorizedException(Exception):
    """Not Authorized Exception"""
    pass

class UserNotFoundException(Exception):
    """User Not Found Exception"""
    pass

class VisitorNotFoundException(Exception):
    """Visitor Not Found Exception"""
    pass