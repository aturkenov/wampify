from contextvars import ContextVar
from typing import Any


class BaseStory:
    """
    """

    def __setattr__(self, k: str, v: Any) -> None:
        self.__dict__[k] = v


class Story(BaseStory):
    """
    Represents
    """


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

