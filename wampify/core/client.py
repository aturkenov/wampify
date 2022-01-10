from typing import *


class Client:
    """
    Represents a requested client (wamp session)

    - `i` - session authid 
    - `role` - session role
    - `session_i` - session number
    """

    i: Any # session authid 
    role: str # session role
    session_i: Any # session identificator

    def __init__(
        self,
        i: Any,
        role: str,
        session_i: Any,
    ):
        self.i = i
        self.role = role
        self.session_i = session_i

