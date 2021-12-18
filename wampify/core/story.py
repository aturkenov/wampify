from contextvars import ContextVar
from .client import *


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
