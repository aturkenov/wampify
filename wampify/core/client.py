from typing import *


class Client:
    """
    Represents
    """

    i: Any
    role: str
    session_i: Any

    def __init__(
        self,
        i: Any,
        role: str,
        session_i: Any,
    ):
        self.i = i
        self.role = role
        self.session_i = session_i