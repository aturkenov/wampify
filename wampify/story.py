from .client import Client
from .background_task import BackgroundTasks
from .request import BaseRequest
from .settings import WampifySettings
from autobahn.wamp import ISession as WAMPIS
from contextvars import ContextVar


class Story:
    """
    Represents
    """

    _settings_: WampifySettings
    _client_: Client
    _wamps_: WAMPIS
    _background_tasks_: BackgroundTasks
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

