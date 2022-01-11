from typing import Any


class ISessionFactory:
    """
    Session Factory Interface
    represents unit of session (AlchemySession, RedisConnection, etc...)
    Go to example/ directory
    """

    async def on_release(self) -> Any:
        """
        If session was requested by user
        """

    async def on_raise(self) -> None:
        """
        If something went wrong
        """

    async def on_close(self) -> None:
        """
        Closes
        """

