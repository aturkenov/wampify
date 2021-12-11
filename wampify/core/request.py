from autobahn.wamp import CallDetails, EventDetails
from contextvars import ContextVar
from typing import *


class Client:
    """
    """

    i: Any
    role: str
    session_i: Any

    def __init__(
        self,
        i: Any,
        role: str,
        session_i: Any,
    ):
        self.i = i
        self.role = role
        self.session_i = session_i


class Story:
    """
    Represents
    """

    client: Client


current_story_context = ContextVar('current_story_context')


def create_story() -> Story:
    """
    """
    story = Story()
    current_story_context.set(story)
    return story


def get_current_story() -> Story:
    """
    Returns current story by context
    """
    return current_story_context.get()


class BaseRequest:
    """
    """

    endpoint: Callable
    A: Iterable[Any]
    K: Mapping[str, Any]
    story: Story
    client: Client

    def __init__(
        self,
        endpoint: Callable,
        A: Iterable[Any] = [],
        K: Mapping[str, Any] = {},
    ):
        self.endpoint = endpoint
        self.A = A
        self.K = K
        self.story = create_story()


class CallRequest(BaseRequest):
    """
    """

    def __init__(
        self,
        endpoint: Callable,
        call_details: CallDetails,
        A: Iterable[Any] = [],
        K: Mapping[str, Any] = {},
    ):
        super().__init__(endpoint=endpoint, A=A, K=K)
        self.client = Client(
            i=call_details.caller_authid,
            role=call_details.caller_authrole,
            session_i=call_details.caller
        )
        self.story.client = self.client


class PublishRequest(BaseRequest):
    """
    """

    def __init__(
        self,
        endpoint: Callable,
        publish_details: EventDetails,
        A: Iterable[Any] = [],
        K: Mapping[str, Any] = {},
    ):
        super().__init__(endpoint=endpoint, A=A, K=K)
        self.client = Client(
            i=publish_details.publisher_authid,
            role=publish_details.publisher_authrole,
            session_i=publish_details.publisher
        )
        self.story.client = self.client

