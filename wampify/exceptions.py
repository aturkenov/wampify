class BaseError(BaseException):
    """
    """
    cause: str


class InvalidPayload(BaseError):
    """
    400
    """


class AuthenticationFailed(BaseError):
    """
    401
    """


class NotAuthenticated(BaseError):
    """
    401
    """
    cause = 'The request requires authentication.'


class Denied(BaseError):
    """
    403
    """
    cause = 'You have no permissions.'


class NotFound(BaseError):
    """
    404
    """
    cause = 'The requested object was not found.'


class TimedOut(BaseError):
    """
    408
    """
    cause = 'Timed out.'


class SomethingWentWrong(BaseError):
    """
    500
    """
    cause = 'I apologize. We are already fixing this problem :('


class SerializationError(SomethingWentWrong):
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


class ExceededRetryCount(Exception):
    """
    """

