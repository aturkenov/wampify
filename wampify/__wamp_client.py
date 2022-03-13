from aiohttp import ClientSession as HTTPClient
import orjson as json
import hmac
import hashlib
import base64
from random import randint
from datetime import datetime
from wampify.exceptions import SomethingWentWrong
from typing import Mapping, Tuple


def _utcnow():
   now = datetime.utcnow()
   return now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class WAMPClient:
    """
    """

    def __init__(
        self,
        caller_url: str,
        publisher_url: str,
        key: str = None,
        secret: str = None,
        timeout: int = 300
    ) -> None:
        assert type(caller_url) == str
        assert type(publisher_url) == str
        assert type(timeout) == int
        self._caller = caller_url
        self._publisher = publisher_url
        self._key = None
        if key:
            assert type(key) == str
            self._key = key
        self._secret = None
        if secret:
            assert type(secret) == str
            self._secret = secret
        self._timeout = timeout
        self._sequence = 1
        self._headers = { 'Content-Type': 'application/json' }

    def _generate_signature(
        self,
        data: bytes
    ) -> Tuple[str, int, str]:
        timestamp = _utcnow()
        nonce = randint(0, 9007199254740992)
        hm = hmac.new(self._secret.encode('utf8'), None, hashlib.sha256)
        hm.update(self._key.encode('utf8'))
        hm.update(timestamp.encode('utf8'))
        hm.update(str(self._sequence).encode('utf8'))
        hm.update(str(nonce).encode('utf8'))
        hm.update(data)
        signature = base64.urlsafe_b64encode(hm.digest())
        return timestamp, nonce, signature.decode('utf8')

    async def call(
        self,
        uri: str,
        *A,
        options: Mapping = {},
        **K
    ):
        """
        """
        body = { 'procedure': uri }
        if A:
            body['args'] = A
        if K:
            body['kwargs'] = K
        if options:
            assert type(options) == dict
            body['options'] = options
        data = json.dumps(body)

        P = { 'seq': self._sequence }
        if self._key:
            P['key'] = self._key
            P['timestamp'], P['nonce'], P['signature'] = self._generate_signature(data)

        self._sequence += 1

        async with HTTPClient(headers=self._headers) as session:
            async with session.post(self._caller, params=P, data=data) as response:
                data = await response.read()
                body = json.loads(data)
                if response.status == 200:
                    return body['args'][0]
                raise SomethingWentWrong(body['error'])

    async def publish(
        self,
        uri: str,
        *A,
        options: Mapping = {},
        **K
    ):
        """
        """
        body = { 'topic': uri }
        if A:
            body['args'] = A
        if K:
            body['kwargs'] = K
        if options:
            assert type(options) == dict
            body['options'] = options
        data = json.dumps(body)

        P = { 'seq': self._sequence }
        if self._key:
            P['key'] = self._key
            P['timestamp'], P['nonce'], P['signature'] = self._generate_signature(data)

        self._sequence += 1

        async with HTTPClient(headers=self._headers) as session:
            async with session.post(self._publisher, params=P, data=data) as response:
                data = await response.read()
                body = json.loads(data)
                if response.status == 200:
                    return body['id']
                raise SomethingWentWrong(body['error'])

