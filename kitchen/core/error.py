from typing import Any


class KBaseError(BaseException):
    """
    """
    _is_already_initialized: bool = False

    name = 'base'
    cause: Any = None

    def __init__(self, cause: Any = ...) -> None:
        if self._is_already_initialized:
            return 
        self._is_already_initialized = True
        if type(cause) != ...:
            self.cause = cause

    def to_primitive(cls):
        return {
            'name': cls.name,
            'cause': cls.cause
        }


class PayloadParseError(KBaseError):
    """
    400
    """

    name = 'payload_parse_error'
    cause = 'The payload must be primitive.'


class PayloadValidationError(KBaseError):
    """
    400
    """

    name = 'payload_validation_error'


class AuthenticationFailed(KBaseError):
    """
    401
    """

    name = 'authentication_failed'


class NotAuthenticated(KBaseError):
    """
    401
    """

    name = 'not_authenticated'
    cause = 'The request requires authentication.'


class PermissionDenied(KBaseError):
    """
    403
    """

    name = 'permission_denied'
    cause = 'You have no permissions.'

class NotFound(KBaseError):
    """
    404
    """

    name = 'not_found'
    cause = 'The requested object was not found.'


class SomethingWentWrong(KBaseError):
    """
    500
    """

    name = 'something_went_wrong'
    cause = 'I apologize. We are already fixing this problem :('


class SerializationError(SomethingWentWrong):
    """
    """

