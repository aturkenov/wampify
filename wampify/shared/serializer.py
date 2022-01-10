from pydantic import BaseModel
import orjson as json
from typing import Any


PRIMITIVES = (
    type(None),
    bytes, 
    bool,
    int, float,
    str,
)


def is_primitive(
    v: Any
) -> bool:
    """
    Is primitive data type?
    """
    return type(v) in PRIMITIVES


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
        data = data.to_primitive() 
    except: ...

    return json.dumps(data)


DEFAULT_SERIALIZERS = [
    serialize_pydantic,
]
