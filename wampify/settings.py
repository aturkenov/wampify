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
    factory: Type = None
    authid: str = None
    authmethods: List[str] = None
    authrole: str = None
    authextra: Any = None
    resumable: str = None
    resume_session: str = None
    resume_token: str = None


class WAMPBackendSettings(BaseModel):
    """
    """
    domain: str = None
    url: AnyUrl = None
    start_loop = True
    session: WAMPBSessionSettings


class KitchenSettings(BaseModel):
    """
    """
    debug = False
    wamp: WAMPBackendSettings


def get_validated_settings(data: Mapping) -> KitchenSettings:
    from core.wamp import WAMPBSession

    class _WAMPBSessionSettings(WAMPBSessionSettings):
        # FIXME
        # factory: WAMPBSession = None
        factory: Any = None

    class _WAMPBackendSettings(WAMPBackendSettings):
        session: _WAMPBSessionSettings

    class _KitchenSettings(KitchenSettings):
        wamp: _WAMPBackendSettings

    return _KitchenSettings(**data)

