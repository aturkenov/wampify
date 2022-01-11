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


class SessionPoolSettings(BaseModel):
    """
    """
    factories = []


class WampifySettings(BaseModel):
    """
    """
    debug = False
    uri_prefix: str = None
    router_url: str = None
    start_loop = True
    wamp_session: WampifySessionSettings
    session_pool: SessionPoolSettings = SessionPoolSettings()


def get_validated_settings(data: Mapping) -> WampifySettings:
    """
    Returns validated user settings
    """
    from core.wamp import AsyncioWampifySession 

    class _WampifySessionSettings(WampifySessionSettings):
        ...
        # FIXME factory: WampifySession = WampifySession

    class _WampifySettings(WampifySettings):
        wamp_session: _WampifySessionSettings

    settings = _WampifySettings(**data)

    if settings.wamp_session.factory is None:
        settings.wamp_session.factory = AsyncioWampifySession

    return settings

