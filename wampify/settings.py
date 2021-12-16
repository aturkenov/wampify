from pydantic import BaseModel, Extra, AnyUrl
from typing import *


class BaseSettings(BaseModel):
    """
    """

    class Config:
        extra = Extra.allow


class EndpointSettings(BaseModel):
    """
    """
    validate_payload = True


class WAMPBSessionSettings(BaseModel):
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


class WAMPBackendSettings(BaseModel):
    """
    """
    domain: str = None
    url: str = None
    start_loop = True
    session: WAMPBSessionSettings


class KitchenSettings(BaseModel):
    """
    """
    debug = False
    wamp: WAMPBackendSettings


def get_validated_settings(data: Mapping) -> KitchenSettings:
    """
    Returns validated user settings
    """
    from core.wamp import WAMPBSession

    class _WAMPBSessionSettings(WAMPBSessionSettings):
        ...
        # FIXME
        # factory: WAMPBSession = WAMPBSession

    class _WAMPBackendSettings(WAMPBackendSettings):
        session: _WAMPBSessionSettings

    class _KitchenSettings(KitchenSettings):
        wamp: _WAMPBackendSettings

    settings = _KitchenSettings(**data)

    if settings.wamp.session.factory is None:
        settings.wamp.session.factory = WAMPBSession
    
    return settings

