
class FailedToUploadImageError(Exception):
    """Failed to upload image to the storage"""
    pass

# UnauthorizedError, ConflictError, AuthenticationError

class UnauthorizedError(Exception):
    """Unauthorized Error"""
    pass

class ConflictError(Exception):
    """Conflict Error"""
    pass

class AuthenticationError(Exception):
    """Authentication Error"""
    pass
