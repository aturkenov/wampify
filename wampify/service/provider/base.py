from ...story import Story, get_current_story


class BaseKProvider:
    """
    """

    story: Story

    def __init__(
        self
    ):
        self.story = get_current_story()


class KProvider(BaseKProvider):
    """
    """

