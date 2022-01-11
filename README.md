# Wampify - WAMP framework

&Web Application Messaging Protocol (WAMP) built under the hood on &WebSocket protocol, so each session has permenent connection with router, сответственно with WAMP you can create and build &decentrialized, &independent and &scalable network of &microservices.

## Features:
- &High performance
- &Remote Procedure Call (RPC) and &Publish & Subscribe (PubSub)
- Payload validation based on &pydantic
- &Serialization (default &binary orjson)
- &Your custom middlewares
- &Signals (WAMP session joined, WAMP session leaved, etc...)
- &Background tasks
- &Session pool (&SQLAlchemy, &Redis, etc...)
- Source code is well documented

# Introduction

`INFO!` Full source code in &example/basic/ directory. More examples &here (a.py is server side and b.py is client side).

Before install, configure and run your WAMP router. I'm recomending to use &Crossbar router

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

## Backgroud Tasks

Main process executes child process when background tasks pushed to queue.

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

```python
@wampify.on
async def wamp_session_joined(): ...

@wampify.on
async def wamp_session_leaved(): ...
```

# TODO:

- Unit tests
- Better payload validation for subscriptions and pattern matching
- Independent signals
- Improved wamp session (user-friendly)
- Wampify serializer
- Background tasks must have wamp session
- Subscription whitelisting and blacklisting
- Progressive calls
- In Memory Cache
- Uvloop support
- Documentation
- Clean Arch
- API Schema generation

# Contribution

Aidar spend time to me pls!