class ALMException(Exception):
    """Base exception for ALM system"""
    pass


class ValidationError(ALMException):
    """Raised when validation fails"""
    pass


class DatabaseError(ALMException):
    """Raised on database operations"""
    pass


class TraceError(ALMException):
    """Raised on trace link operations"""
    pass


class EntityNotFoundError(ALMException):
    """Raised when entity is not found"""
    pass
