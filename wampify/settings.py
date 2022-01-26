from pydantic import BaseModel, Extra 
from typing import *


class BaseSettings(BaseModel):
    """
    """

    class Config:
        extra = Extra.allow


class EndpointOptions(BaseModel):
    """
    """

    validate_payload = True


class WampifySessionSettings(BaseModel):
    """
    """

    realm: str
    factory: Any = None
    authid: str = None
    authrole: str = None
    authmethods: List[str] = None
    authextra: Any = None
    resumable: str = None
    resume_session: str = None
    resume_token: str = None
    show_registered = False
    show_subscribed = False


class WampifySettings(BaseModel):
    """
    """

    debug = False
    router_url: str = None
    start_loop = True
    uri_prefix: str = None
    wamps: WampifySessionSettings


def get_validated_settings(**KW) -> WampifySettings:
    """
    Returns validated user settings
    """
    from .wamp import AsyncioWampifySession 

    class _WampifySessionSettings(WampifySessionSettings):
        ...
        # FIXME factory: WampifySession = WampifySession

    class _WampifySettings(WampifySettings):
        wamps: _WampifySessionSettings

    settings = _WampifySettings(**KW)

    if settings.wamps.factory is None:
        settings.wamps.factory = AsyncioWampifySession

    return settings

