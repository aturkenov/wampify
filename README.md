# Wampify - High-Level WAMP framework

![license](https://img.shields.io/github/license/aturkenov/wampify)
![package-version](https://img.shields.io/pypi/v/wampify)
![pyversions](https://img.shields.io/pypi/pyversions/wampify)

Provides an opportunity for better interaction with Web Application Messaging Protocol. It offers a variety of tools (background tasks, scheduling, signals, middlewares, etc...) that enable one to create a platform of independent applications. Built on top of [autobahn library](https://autobahn.readthedocs.io/en/latest/index.html).

## Features:
- [High performance](https://github.com/aturkenov/wampify/tree/main/example/benchmark)
- [Remote Procedure Calls (RPC)](https://github.com/aturkenov/wampify#remote-procedure-call-rpc) and [Publish & Subscribe (PubSub)](https://github.com/aturkenov/wampify#publish--subscribe-pubsub)
- [Payload validation](https://pydantic-docs.helpmanual.io/usage/validation_decorator/) based on python [pydantic library](https://pydantic-docs.helpmanual.io)
- [Signals (WAMP session joined, WAMP session leaved, etc...)](https://github.com/aturkenov/wampify#signals)
- [Middlewares](https://github.com/aturkenov/wampify#custom-middlewares)
- [Background tasks](https://github.com/aturkenov/wampify#backgroud-tasks)
- [Scheduling](https://github.com/aturkenov/wampify#scheduling) based on python [schedule library]()
- Source code is well documented

# Introduction

[Web Application Messaging Protocol (WAMP)](https://wamp-proto.org/intro.html) is an open standard WebSocket subprotocol that provides two messaging patterns in one Web native protocol:

- [routed Remote Procedure Calls (RPC)](https://github.com/aturkenov/wampify#remote-procedure-call-rpc)
- [Publish & Subscribe (PubSub)](https://github.com/aturkenov/wampify#publish--subscribe-pubsub)

The [WebSocket protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) brings bi-directional (soft) real-time and wire traffic efficient connections to the browser. Today (2022) WebSocket is universally supported in browsers, network equipment, servers and client languages.

Using WAMP you can build distributed systems which are loosely coupled and communicate in (soft) real-time.

`INFO!` Full source code in [example/basic/ directory](https://github.com/aturkenov/wampify/tree/main/example/basic) (`a.py` is server side and `b.py` is client side). More examples [here](https://github.com/aturkenov/wampify/tree/main/example).

Before install and configure your [WAMP router](https://wamp-proto.org/implementations.html#routers). I'm recomending to use [Crossbar router](https://crossbar.io). More about crossbar configuration [here](https://crossbar.io/docs/Getting-Started/#crossbar-configuration).

```bash
pip install crossbar
crossbar init
```

```bash
pip install wampify
```

Initialize Wampify application, pass `preuri` (URI prefix), WAMP router URL, WAMP session realm and WAMP session authentication (by default anonymous).

```python
from wampify import Wampify

wampify = Wampify(
    debug=True,
    preuri='com.example',
    router={
        'url': 'ws://127.0.0.1:8080/private'
    },
    wamps={
        'realm': 'example',
        'authid': 'application',
        'authmethods': ['anonymous'],
        'authrole': 'private',
        'show_registered': True,
        'show_subscribed': True
    }
)

@wampify.subscribe
async def hello(name: str = 'Anonymous'):
    print(f'{name} you are welcome!')

if __name__ == '__main__':
    wampify.run()
```

`IMPORTANT!` Don't forget to disable debug mode in production. (default `debug=False`)

Finally, run router `crossbar start` and application `python application.py` in different terminal sessions.

## Remote Procedure Calls (RPC)

A Caller issues calls to remote procedures by providing the procedure URI and any arguments for the call. The Callee will execute the procedure using the supplied arguments to the call and return the result of the call to the Caller.

Callees register procedures they provide with Dealers. Callers initiate procedure calls first to Dealers. Dealers route calls incoming from Callers to Callees implementing the procedure called, and route call results back from Callees to Callers.

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

A Publishers publishes events to topics by providing the topic URI and any payload for the event. Subscribers of the topic will receive the event together with the event payload.

Subscribers subscribe to topics they are interested in with Brokers. Publishers initiate publication first at Brokers. Brokers route events incoming from Publishers to Subscribers that are subscribed to respective topics.

It will executes when someone publish something to `com.example.hello`

```python
@wampify.subscribe
async def hello(name: str = 'Anonymous'):
    print(f'{name} you are welcome!')
```

# Advanced

## Story

Like Request object Story represents request details: caller or publisher details (if not disclosed), sent time and event type.

All required resources (as WAMP Session, Background tasks, ...) bind to Story instance.

How to get current Story instance?
Just `import * from wampify.story` module and call `get_current_story()` in your procedure.

### Use WAMP session in procedure

```python
...
from wampify.story import *

@wampify.subscribe
async def hello(name: str = 'Anonymous'):
    story = get_current_story()
    story._wamps_.call(
        'com.another_application.client.counter.increment'
    )
    print(f'{name} you are welcome!')

...
```

This example increment clients counter in another application (or microservice) via calling remote procedure, when someone publishes event to `com.example.hello` topic.

## Background Tasks

It's useful for operations that need to happen after a request, but that client doesn't really have to be waiting for operation to complete before receiving response. Also cpu intensive operations can be executed in separated thread.

Mount wampify background task module by passing instance of Wampify, then define required procedure and pass it as `story._background_tasks_.add($REQUIRED_PROCEDURE)`.

```python
from wampify import Wampify, background_task
from wampify.story import *

wampify = Wampify(...)

background_task.mount(wampify)

async def task():
    print('im here')

@wampify.register
async def asap():
    story = get_current_story()
    story._background_tasks_.add(task)
    print('background task pushed to queue')

if __name__ == '__main__':
    wampify.run()
```

More examples [here](https://github.com/aturkenov/wampify/tree/main/example/background_task/).

## Scheduling

Run anything periodically using a friendly syntax.

Before install dependencies. More about library [here](https://schedule.readthedocs.io/en/stable/).

```bash
pip install schedule
```

Mount wampify scheduling module by passing instance of Wampify, then define required procedure and pass it as `wampify.schedule.every($INTERVAL).$TIME_UNIT.do($REQUIRED_PROCEDURE)`

```python
from wampify import Wampify, scheduling

wampify = Wampify(...)

scheduling.mount(wampify)

async def send_message_every_day(): ...

wampify.schedule.every().day.do(send_message_every_day)

if __name__ == '__main__':
    wampify.run()
```

More examples [here](https://github.com/aturkenov/wampify/tree/main/example/scheduling/).

## Signals (Events)

Signals allow certain senders to notify listeners. For example subscribe to wamp session `joined` or `leaved` events via `@wamps_signals.on` decorator.

```python
from wampify import Wampify
from wampify.signals import wamps_signals

wampify = Wampify(...)

@wamps_signals.on
async def joined(): ...

@wamps_signals.on
async def leaved(): ...

if __name__ == '__main__':
    wampify.run()
```

More examples [here](https://github.com/aturkenov/wampify/tree/main/example/signal/)

## Middlewares

A "middleware" is a behavior that works with every request before it is processed by any specific procedure. And also with every response before returning it.

For example `TimeoutMiddleware`. it raises `TimedOut` error if procedure runtime overflow `n` seconds

```python
from wampify import Wampify
from wampify.middleware.timeout import TimeoutMiddleware

wampify = Wampify(
    debug=False,
    preuri='com.example',
    router={ 'url': 'ws://127.0.0.1:8765/private' },
    wamps={
        'realm': 'example',
        'show_registered': True,
        'show_subscribed': True
    },
    middlewares={
        'timeout': { 'duration': 60 }
    }
)

wampify.add_middleware(TimeoutMiddleware)

if __name__ == '__main__':
    wampify.run()
```

More examples [here](https://github.com/aturkenov/wampify/tree/main/example/middleware/)

## How to connect SQLAlchemy?

```python
from wampify import Wampify
from wampify.signals import entrypoint_signals

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

wampify = Wampify(...)

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

@wampify.subscribe
async def hello(name: str = 'Anonymous'):
    story = get_current_story()
    STMT = "select * from test"
    print(await story.alchemy.execute(STMT))

...
```

# TODO:

- Benchmarking
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