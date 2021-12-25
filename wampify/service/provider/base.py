from core.story import *


class BaseProvider:
    """
    """

    _story: Story

    def __init__(
        self
    ):
        self._story = get_current_story()

