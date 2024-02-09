
class FailedToUploadImageError(Exception):
    """Failed to upload image to the storage"""


class UnauthorizedError(Exception):
    """Unauthorized Error"""

class ConflictError(Exception):
    """Conflict Error"""

class AuthenticationError(Exception):
    """Authentication Error"""

class CardAlreadyExistsError(Exception):
    """Card Already Exists Error"""

class InvalidCardIdError(Exception):
    """Invalid Card Id Error"""

class NotAuthorizedException(Exception):
    """Not Authorized Exception"""

class UserNotFoundException(Exception):
    """User Not Found Exception"""

class VisitorNotFoundException(Exception):
    """Visitor Not Found Exception"""
