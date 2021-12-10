from pydantic import BaseModel, Extra, AnyUrl
from typing import *


class BaseSettings(BaseModel):
    """
    """

    class Config:
        extra = Extra.allow


class RCSettings(BaseModel):
    """
    """

    disabled = False



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
    serializers: List[Callable] = []
    RCs: List[Any] = []


def get_validated_settings(data: Mapping) -> KitchenSettings:
    from core.wamp import WAMPBSession
    from rchain import RChain, DEFAULT_RCHAINS
    from shared.serializer import DEFAULT_SERIALIZERS

    class _WAMPBSessionSettings(WAMPBSessionSettings):
        # FIXME
        # factory: WAMPBSession = None
        factory: Any = None


    class _WAMPBackendSettings(WAMPBackendSettings):
        session: _WAMPBSessionSettings


    class _KitchenSettings(KitchenSettings):
        wamp: _WAMPBackendSettings
        serializers: List[Callable] = DEFAULT_SERIALIZERS
        # FIXME
        # RCs: List[RChain] = DEFAULT_RCHAINS
        RCs: List[Any] = DEFAULT_RCHAINS

    return _KitchenSettings(**data)

