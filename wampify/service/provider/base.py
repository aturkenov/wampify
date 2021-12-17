from core.request import *


class BaseProvider:
    """
    """

    story: Story

    def __init__(
        self
    ):
        self.story = get_current_story()


class Provider(BaseProvider):
    """
    """

