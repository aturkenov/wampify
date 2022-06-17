from pydantic import BaseModel, Extra 
from typing import Callable, Any, List, Mapping


class _BaseModel(BaseModel):
    """
    """

    class Config:
        extra = Extra.allow


class EndpointOptions(_BaseModel):
    """
    """

    payload: Mapping = {}
    middlewares: Mapping = {}


class RegisterEndpointOptions(EndpointOptions):
    """
    """


class SubscribeEndpointOptions(EndpointOptions):
    """
    """


def wamps_on_challenge(challenge): ...


class WampifySessionSettings(_BaseModel):
    """
    """

    realm: str
    authid: str = None
    authrole: str = None
    authmethods: List[str] = None
    authextra: Any = None
    on_challenge: Callable = wamps_on_challenge
    resumable: str = None
    resume_session: str = None
    resume_token: str = None
    show_registered = False
    show_subscribed = False
    factory: Any = None


class RouterSettings(_BaseModel):
    """
    """

    url: str = None


class WampifySettings(_BaseModel):
    """
    """

    debug = False
    preuri: str
    router: RouterSettings
    start_loop = True
    wamps: WampifySessionSettings
    middlewares: Mapping = {}


def get_validated_settings(**kwargs) -> WampifySettings:
    """
    Returns validated user settings
    """
    class _WampifySessionSettings(WampifySessionSettings):
        ...
        # FIXME factory: WampifySession = WampifySession

    class _WampifySettings(WampifySettings):
        wamps: _WampifySessionSettings

    settings = _WampifySettings(**kwargs)

    if settings.wamps.factory is None:
        from wampify.wamp import AsyncioWampifySession
        settings.wamps.factory = AsyncioWampifySession

    return settings

