from aiohttp import ClientSession as HTTPClient
import orjson as json
import hmac
import hashlib
import base64
from random import randint
from datetime import datetime
from wampify.exceptions import SomethingWentWrong
from typing import Mapping


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
        assert type(key) == str
        assert type(secret) == str
        assert type(timeout) == int
        self._caller = caller_url
        self._publisher = publisher_url
        self._key = key
        self._secret = secret
        self._timeout = timeout
        self._sequence = 1
        self._headers = { 'Content-Type': 'application/json' }

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

        params = {
            'timestamp': _utcnow(),
            'seq': self._sequence
        }
        if self._key:
            params['key'] = self._key
            params['nonce'] = randint(0, 9007199254740992)
            hm = hmac.new(self._secret.encode('utf8'), None, hashlib.sha256)
            hm.update(params['key'].encode('utf8'))
            hm.update(params['timestamp'].encode('utf8'))
            hm.update(str(params['seq']).encode('utf8'))
            hm.update(str(params['nonce']).encode('utf8'))
            hm.update(data)
            signature = base64.urlsafe_b64encode(hm.digest())
            params['signature'] = signature.decode('utf8')

        self._sequence += 1

        async with HTTPClient(headers=self._headers) as session:
            async with session.post(self._caller, params=params, data=data) as response:
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

        params = {
            'timestamp': _utcnow(),
            'seq': self._sequence
        }
        if self._key:
            params['key'] = self._key
            params['nonce'] = randint(0, 9007199254740992)
            hm = hmac.new(self._secret.encode('utf8'), None, hashlib.sha256)
            hm.update(params['key'].encode('utf8'))
            hm.update(params['timestamp'].encode('utf8'))
            hm.update(str(params['seq']).encode('utf8'))
            hm.update(str(params['nonce']).encode('utf8'))
            hm.update(data)
            signature = base64.urlsafe_b64encode(hm.digest())
            params['signature'] = signature.decode('utf8')

        self._sequence += 1

        async with HTTPClient(headers=self._headers) as session:
            async with session.post(self._publisher, params=params, data=data) as response:
                data = await response.read()
                body = json.loads(data)
                if response.status == 200:
                    return body['id']
                raise SomethingWentWrong(body['error'])

