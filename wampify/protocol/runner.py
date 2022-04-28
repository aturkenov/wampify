"""
https://github.com/isra17/autobahn-autoreconnect
"""
import asyncio
import signal
from autobahn.wamp.types import ComponentConfig
from autobahn.websocket.util import parse_url
from autobahn.asyncio.websocket import WampWebSocketClientFactory
from wampify.exceptions import ExceededRetryCount


class Runner(object):
    """
    This class is a slightly modified version of autobahn.asyncio.wamp.ApplicationRunner
    with auto reconnection feature to with customizable strategies.
    """

    def __init__(self, url, realm, extra=None, serializers=None, debug_app=False,
                 ssl=None, loop=None, reconnect_strategy=BackoffStrategy(), open_handshake_timeout=30, auto_ping_interval=10, auto_ping_timeout=27):
        """
        :param url: The WebSocket URL of the WAMP router to connect to (e.g. `ws://somehost.com:8090/somepath`)
        :type url: unicode
        :param realm: The WAMP realm to join the application session to.
        :type realm: unicode
        :param extra: Optional extra configuration to forward to the application component.
        :type extra: dict
        :param serializers: A list of WAMP serializers to use (or None for default serializers).
           Serializers must implement :class:`autobahn.wamp.interfaces.ISerializer`.
        :type serializers: list
        :param debug_app: Turn on app-level debugging.
        :type debug_app: bool
        :param ssl: An (optional) SSL context instance or a bool. See
           the documentation for the `loop.create_connection` asyncio
           method, to which this value is passed as the ``ssl=``
           kwarg.
        :type ssl: :class:`ssl.SSLContext` or bool
        :param open_handshake_timeout: How long to wait for the opening handshake to complete (in seconds).
        :param auto_ping_interval: How often to send a keep-alive ping to the router (in seconds).
           A value of None turns off pings.
        :type auto_ping_interval: int
        :param auto_ping_timeout: Consider the connection dropped if the router does not respond to our
           ping for more than X seconds.
        :type auto_ping_timeout: int
        """
        self._url = url
        self._realm = realm
        self._extra = extra or dict()
        self._debug_app = debug_app
        self._serializers = serializers
        self._loop = loop or asyncio.get_event_loop()
        self._reconnect_strategy = reconnect_strategy
        self._closing = False
        self._open_handshake_timeout = open_handshake_timeout
        self._auto_ping_interval = auto_ping_interval
        self._auto_ping_timeout = auto_ping_timeout

        self._isSecure, self._host, self._port, _, _, _ = parse_url(url)

        if ssl is None:
            self._ssl = self._isSecure
        else:
            if ssl and not self._isSecure:
                raise RuntimeError(
                    'ssl argument value passed to %s conflicts with the "ws:" '
                    'prefix of the url argument. Did you mean to use "wss:"?' %
                    self.__class__.__name__)
            self._ssl = ssl

    def run(
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs, start_loop=False)

    async def _connect(self):
        self._active_protocol = None
        self._reconnect_strategy.reset_retry_interval()
        while True:
            try:
                _, protocol = await self._loop.create_connection(self._transport_factory, self._host, self._port, ssl=self._ssl)
                protocol.is_closed.add_done_callback(self._reconnect)
                self._active_protocol = protocol
                return
            except OSError:
                print('Connection failed')
                if self._reconnect_strategy.retry():
                    retry_interval = self._reconnect_strategy.get_retry_interval()
                    print('Retry in {} seconds'.format(retry_interval))
                    await asyncio.sleep(retry_interval)
                else:
                    print('Exceeded retry count')
                    self._loop.stop()
                    raise ExceededRetryCount()

                self._reconnect_strategy.increase_retry_interval()

    def _reconnect(self, f):
        # Reconnect
        print('Connection lost')
        if not self._closing:
            print('Reconnecting')
            asyncio.run_coroutine_threadsafe(self._connect(), loop=self._loop)

    def stop(self, *args):
        self._loop.stop()

