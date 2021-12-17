import functools
from twisted.internet.defer import ensureDeferred


def ensure_deferred(f):
    """
    Converts asyncio coroutine to twisted.inlineCallback
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        return ensureDeferred(result)
    return wrapper

