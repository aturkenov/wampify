class IReconnectStrategy:

    def get_retry_interval(
        self
    ):
        raise NotImplementedError()

    def reset_retry_interval(
        self
    ):
        raise NotImplementedError()

    def increase_retry_interval(
        self
    ):
        raise NotImplementedError()

    def retry(
        self
    ):
        raise NotImplementedError()


class NoRetryStrategy(IReconnectStrategy):

    def reset_retry_interval(
        self
    ):
        """
        """

    def retry(
        self
    ):
        return False


class BackoffStrategy(IReconnectStrategy):

    def __init__(
        self,
        initial_interval=0.5,
        max_interval=512,
        factor=2
    ):
        self._initial_interval = initial_interval
        self._retry_interval = initial_interval
        self._max_interval = max_interval
        self._factor = factor

    def get_retry_interval(
        self
    ):
        return self._retry_interval

    def reset_retry_interval(
        self
    ):
        self._retry_interval = self._initial_interval

    def increase_retry_interval(
        self
    ):
        self._retry_interval *= self._factor

    def retry(
        self
    ):
        return self._retry_interval <= self._max_interval

