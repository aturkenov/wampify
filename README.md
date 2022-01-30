# Wampify - WAMP framework

![license](https://img.shields.io/github/license/aturkenov/wampify)

[Web Application Messaging Protocol (WAMP)](https://wamp-proto.org/intro.html) is an open standard WebSocket subprotocol that provides two messaging patterns in one Web native protocol:

- [routed Remote Procedure Calls (RPC)](https://github.com/aturkenov/wampify#remote-procedure-call-rpc)
- [Publish & Subscribe (PubSub)](https://github.com/aturkenov/wampify#publish--subscribe-pubsub)

The [WebSocket protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) brings bi-directional (soft) real-time and wire traffic efficient connections to the browser. Today (2022) WebSocket is universally supported in browsers, network equipment, servers and client languages.

Using WAMP you can build distributed systems which are loosely coupled and communicate in (soft) real-time.

Wampify built on top of [autobahn library](https://autobahn.readthedocs.io/en/latest/index.html)

## Features:
- [High performance](https://github.com/aturkenov/wampify/tree/main/example/benchmark)
- [Remote Procedure Calls (RPC)](https://github.com/aturkenov/wampify#remote-procedure-call-rpc) and [Publish & Subscribe (PubSub)](https://github.com/aturkenov/wampify#publish--subscribe-pubsub)
- [Payload validation](https://pydantic-docs.helpmanual.io/usage/validation_decorator/) based on [pydantic](https://pydantic-docs.helpmanual.io)
- [Serialization](https://github.com/aturkenov/wampify#serialization) (default [binary orjson](https://github.com/ijl/orjson))
- [Signals (WAMP session joined, WAMP session leaved, etc...)](https://github.com/aturkenov/wampify#signals)
- [Background tasks](https://github.com/aturkenov/wampify#backgroud-tasks)
- [Custom middlewares](https://github.com/aturkenov/wampify#custom-middlewares)
- Source code is well documented

# Introduction

`INFO!` Full source code in [example/basic/ directory](https://github.com/aturkenov/wampify/tree/main/example/basic) (`a.py` is server side and `b.py` is client side). More examples [here](https://github.com/aturkenov/wampify/tree/main/example).

Before install, configure and run your [WAMP router](https://wamp-proto.org/implementations.html#routers). I'm recomending to use [Crossbar router](https://crossbar.io)

```bash
pip install crossbar
```

In root directory with `.crossbar/` execute

```bash
crossbar start
```

Initialize Wampify application, then pass domain (URI prefix), your WAMP router URL, WAMP session realm and WAMP session authentication (anonymous).

```python
from wampify import Wampify

wampify = Wampify(
    debug=True,
    uri_prefix='com.example',
    router_url='ws://127.0.0.1:8080/private',
    wamps={
        'realm': 'example',
        'authid': None,
        'authmethods': ['anonymous'],
        'authrole': 'private',
        'show_registered': True,
        'show_subscribed': True
    }
)
```

`IMPORTANT!` Don't forget to disable debug mode in production. (default `debug=False`)

## WAMP authentication


## Remote Procedure Calls (RPC)

(https://wamp-proto.org/faq.html#what-is-rpc)

By default Wampify validates input payload if type annotations are defined and takes procedure name as URI segment

It will executes when someone call `com.example.pow`

```python
@wampify.register
async def pow(x: float = 1):
    return x ** 2
```

But you can disable payload validation

```python
@wampify.register(settings={ 'validate_payload': False })
```

Change to another URI

```python
@wampify.register('math.square')
```

## Publish & Subscribe (PubSub)

(https://wamp-proto.org/faq.html#what-is-pubsub)

It will executes when someone publish something to `com.example.hello`

```python
@wampify.subscribe
async def hello(name: str = 'Anonymous'):
    print(f'{name} you are welcome!')
```

## Finally run it

```python
if __name__ == '__main__':
    wampify.run()
```

# Advanced

## Story

## Use WAMP session in procedure

```python
from wampify.story import *

@wampify.subscribe
async def hello(name: str = 'Anonymous'):
    story = get_current_story()
    story._wamps_.call(
        'com.another_microservice.increment_clients_counter'
    )
    print(f'{name} you are welcome!') 
```

## Serialization

## Backgroud Tasks

```python
from wampify.story import *

def asap(): ...

@wampify.subscribe
async def hello(name: str = 'Anonymous'):
    story = get_current_story()
    story._background_tasks_.add(asap)
    print(f'{name} you are welcome!') 
```

## Signals

```python
from wampify.signal_manager import wamps_signals

@wamps_signals.on
async def joined(): ...

@wamps_signals.on
async def leaved(): ...
```

## Custom Middlewares


## How to connect SQLAlchemy?

```python
from wampify.signal_manager import entrypoint_signals

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine('postgresql+asyncpg://scott:tiger@localhost/test', echo=True)

AlchemySession = sessionmaker(engine, AsyncSession)

@entrypoint_signals.on
async def opened(story):
    story.alchemy = AlchemySession()
    print('SQLAlchemy Async Session initialized')

@entrypoint_signals.on
async def raised(story, e):
    await story.alchemy.rollback()
    await story.alchemy.close()
    print('SQLAlchemy Async Session rollback')

@entrypoint_signals.on
async def closed(story):
    await story.alchemy.commit()
    await story.alchemy.close()
    print('SQLAlchemy Async Session closed')
```

## Redis

# Benchmarks


# TODO:

- Unit tests
- Better payload validation for subscriptions and pattern matching
- Subscription white/black listing
- Wampify serializer
- Background tasks must have wamp session
- Progressive calls
- In Memory Cache
- Uvloop support
- Documentation
- Clean Arch
- API Schema generation

# Contribution

https://stackoverflow.com/users/13774052/aidar-turkenov

https://stackoverflow.com/questions/tagged/wamp

https://stackoverflow.com/questions/tagged/wampify

https://github.com/aturkenov/wampify/discussions

https://github.com/aturkenov/wampify/issues

a.k.turken0v@gmail.com