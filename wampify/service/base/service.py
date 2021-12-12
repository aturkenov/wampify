from core.request import *
from typing import *


class BaseWService:
    """
    """

    story: Story

    def __init__(
        self
    ):
        self.story = get_current_story()

