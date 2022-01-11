# Wampify - WAMP framework

[Web Application Messaging Protocol (WAMP)](https://wamp-proto.org/intro.html) is an open standard WebSocket subprotocol that provides two messaging patterns in one Web native protocol:

- [routed Remote Procedure Calls (RPC)](https://github.com/aturkenov/wampify#remote-procedure-call-rpc)
- [Publish & Subscribe (PubSub)](https://github.com/aturkenov/wampify#publish--subscribe-pubsub)

The [WebSocket protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) brings bi-directional (soft) real-time and wire traffic efficient connections to the browser. Today (2022) WebSocket is universally supported in browsers, network equipment, servers and client languages.

Using WAMP you can build distributed systems which are loosely coupled and communicate in (soft) real-time.

## Features:
- [High performance](https://github.com/aturkenov/wampify/tree/main/example/benchmark)
- [Remote Procedure Calls (RPC)](https://github.com/aturkenov/wampify#remote-procedure-call-rpc) and [Publish & Subscribe (PubSub)](https://github.com/aturkenov/wampify#publish--subscribe-pubsub)
- [Payload validation](https://pydantic-docs.helpmanual.io/usage/validation_decorator/) based on [pydantic](https://pydantic-docs.helpmanual.io)
- [Session pool](https://github.com/aturkenov/wampify#session-pool) ([SQLAlchemy](https://www.sqlalchemy.org), [Redis](https://redis.io), etc...)
- [Serialization](https://github.com/aturkenov/wampify#serialization) (default [binary orjson](https://github.com/ijl/orjson))
- [Signals (WAMP session joined, WAMP session leaved, etc...)](https://github.com/aturkenov/wampify#signals)
- [Background tasks](https://github.com/aturkenov/wampify#backgroud-tasks)
- [Custom middlewares](https://github.com/aturkenov/wampify#custom-middlewares)
- Source code is well documented

# Introduction

`INFO!` Full source code in [example/basic/ directory](https://github.com/aturkenov/wampify/tree/main/example/basic). More examples [here](https://github.com/aturkenov/wampify/tree/main/example) (`a.py` is server side and `b.py` is client side).

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
from wampify.core.wampify import Wampify

wampify = Wampify(
    settings={
        'debug': True,
        'wamp': {
            'domain': 'com.example',
            'router_url': 'ws://127.0.0.1:8080/private',
            'session': {
                'realm': 'example',
                'authid': None,
                'authmethods': ['anonymous'],
                'authrole': 'private',
                'show_registered': True,
                'show_subscribed': True
            }
        }
    }
)
```

`IMPORTANT!` Don't forget to disable debug mode in production. (default `debug=False`)

## WAMP authentication

TODO! Here must be about wamp authentication

## Remote Procedure Call (RPC)

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

TODO Here must be something about pattern matching

## Finally run it

```python
if __name__ == '__main__':
    wampify.run()
```

# Advanced

## Story

TODO! Here describe story

## Use WAMP session in procedure

```python
from wampify.core.story import *

@wampify.subscribe
async def hello(name: str = 'Anonymous'):
    story = get_current_story()
    story.wamp_session.call(
        'com.another_microservice.increment_clients_counter'
    )
    print(f'{name} you are welcome!') 
```

## Session pool

Describe about session factory interface and how it works

## Serialization

Describe how it works and that's all

## Backgroud Tasks

Main process executes child process when background tasks pushed to queue.

Describe, how to connect another session

```python
from wampify.core.story import *

def asap(): ...

@wampify.subscribe
async def hello(name: str = 'Anonymous'):
    story = get_current_story()
    story.background_tasks.add(asap)
    print(f'{name} you are welcome!') 
```

## Signals

Describe more about custom signals and firing

```python
@wampify.on
async def wamp_session_joined(): ...

@wampify.on
async def wamp_session_leaved(): ...
```

## Custom Middlewares

Describe how you can use it

# TODO:

- Unit tests
- Better payload validation for subscriptions and pattern matching
- Wampify serializer
- Background tasks must have wamp session
- Subscription white/black listing
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

https://github.com/aturkenov/wampify/issues

a.k.turken0v@gmail.com