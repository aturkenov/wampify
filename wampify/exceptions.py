from typing import Any


class BaseError(BaseException):
    """
    """

    _is_already_initialized = False

    name = 'base'
    cause: Any = None

    def __init__(self, cause: Any = None) -> None:
        if self._is_already_initialized:
            return
        self._is_already_initialized = True
        if cause is not None:
            self.cause = cause

    def to_primitive(
        klass
    ):
        return {
            'name': klass.name,
            'cause': klass.cause
        }


class PayloadParseError(BaseError):
    """
    400
    """

    name = 'payload_parse_error'
    cause = 'The payload must be primitive.'


class PayloadValidationError(BaseError):
    """
    400
    """

    name = 'payload_validation_error'


class AuthenticationFailed(BaseError):
    """
    401
    """

    name = 'authentication_failed'


class NotAuthenticated(BaseError):
    """
    401
    """

    name = 'not_authenticated'
    cause = 'The request requires authentication.'


class PermissionDenied(BaseError):
    """
    403
    """

    name = 'permission_denied'
    cause = 'You have no permissions.'

class NotFound(BaseError):
    """
    404
    """

    name = 'not_found'
    cause = 'The requested object was not found.'


class TimedOut(BaseError):
    """
    408
    """

    name = 'timed_out'
    cause = 'Timed out'

class SomethingWentWrong(BaseError):
    """
    500
    """

    name = 'something_went_wrong'
    cause = 'I apologize. We are already fixing this problem :('


class SerializationError(SomethingWentWrong):
    """
    500
    """


class MiddlewareNotBoundError(SomethingWentWrong):
    """
    500
    """


class FactoryDoesNotExist(SomethingWentWrong):
    """
    500
    """


class WAMPClientHasNotJoinedYet(SomethingWentWrong):
    """
    500
    """


class WAMPCouldNotParseMessage(SomethingWentWrong):
    """
    500
    """

