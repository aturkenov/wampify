from wampify import Wampify, scheduler
import dill as pickling
import hmac
import hashlib


SECRET = b'RSg4p6EYoTGLP51K5gmP3OFbj1R2YJjDNaiO0AAKIeAfFtLE1echPzukazNLSF0A'


wampify = Wampify(
    debug=False,
    urip='__wampify__',
    router={ 'url': 'ws://127.0.0.1:8080/private' },
    wamps={
        'realm': 'example',
        'show_registered': True,
        'show_subscribed': True
    }
)


scheduler.mount(wampify)


@wampify.register
async def call(
    digest: bytes,
    pickled: bytes
):
    actual_digest = hmac.new(SECRET, pickled, hashlib.sha256).digest()
    if digest != actual_digest:
        raise

    function = pickling.loads(pickled)

    await function()


def a():
    print('a')


async def b():
    print('b')


# wampify.schedule.every(2).seconds.do(a)
# wampify.schedule.every(3).seconds.do(b)


if __name__ == '__main__':
    wampify.run()

