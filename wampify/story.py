from typing import TYPE_CHECKING
from contextvars import ContextVar
from autobahn.wamp import ISession as WAMPIS
if TYPE_CHECKING:
    from wampify.requests import BaseRequest
    from wampify.endpoints import Endpoint
    from wampify.settings import WampifySettings


class Story:
    """
    Represents
    """

    _wamps_: WAMPIS
    _request_: 'BaseRequest'
    _endpoint_: 'Endpoint'
    _settings_: 'WampifySettings'


current_story_context = ContextVar('current_story_context')


def create_story() -> Story:
    story = Story()
    current_story_context.set(story)
    return story


def get_current_story() -> Story:
    """
    Returns current story by context
    """
    return current_story_context.get()

