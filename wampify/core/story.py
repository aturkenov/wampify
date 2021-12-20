from .client import *
from .session_pool import *
from .background_task import *
from contextvars import ContextVar


class Story:
    """
    Represents
    """

    client: Client
    session_pool: SessionPool
    background_tasks: BackgroundTasks


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

