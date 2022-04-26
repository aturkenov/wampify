from wampify.requests import BaseRequest
from wampify.settings import WampifySettings, EndpointOptions
from autobahn.wamp import ISession as WAMPIS
from contextvars import ContextVar


class Story:
    """
    Represents
    """

    _settings_: WampifySettings
    _wamps_: WAMPIS
    _request_: BaseRequest
    _endpoint_options_: EndpointOptions


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

