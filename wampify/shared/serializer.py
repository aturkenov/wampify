from pydantic import BaseModel
import orjson as json
from typing import *


def serialize_pydantic(
    instance: BaseModel
) -> bytes:
    """
    """
    return instance.json(instance, default=json)


def serialize_primitive(
    data: Any
) -> bytes:
    """
    """
    try:
        return data.to_primitive()
    except:
        return json.dumps(data)


DEFAULT_SERIALIZERS = [
    serialize_pydantic,
]
