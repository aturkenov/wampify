from wampify.client import Client
from wampify.requests import BaseRequest
from wampify.settings import WampifySettings
from autobahn.wamp import ISession as WAMPIS
from contextvars import ContextVar


class Story:
    """
    Represents
    """

    _settings_: WampifySettings
    _client_: Client
    _wamps_: WAMPIS
    _request_: BaseRequest


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

