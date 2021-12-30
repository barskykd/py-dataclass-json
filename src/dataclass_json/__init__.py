import datetime
import enum
from dataclasses import is_dataclass, fields
from typing import Dict, List, Type, TypeVar

from ._impl import TypeInspector, NonJsonableValueError

T = TypeVar('T')


def from_dict(t: Type[T], d: Dict) -> T:
    return __json_val_to_t(d, TypeInspector(t))


def from_list(t: Type[T], d: List) -> List[T]:
    return __json_val_to_t(d, TypeInspector(List[t]))


def to_dict(o: object) -> Dict:
    return __val_to_json_val(o)


def to_list(o: List[T]) -> List:
    return __val_to_json_val(o)


def __data_class_to_dict(x):
    assert is_dataclass(x)
    result = {}
    for f in fields(x):
        result[f.name] = __val_to_json_val(getattr(x, f.name))
    return result


def __named_tuple_to_dict(x):
    # noinspection PyProtectedMember
    return {k: __val_to_json_val(getattr(x, k)) for k in x._fields}


def __val_to_json_val(v):
    if v is None:
        return v
    if isinstance(v, (int, float, str, bool)):
        return v
    if isinstance(v, datetime.datetime):
        return v.isoformat()
    if isinstance(v, list):
        return [__val_to_json_val(x) for x in v]
    if isinstance(v, dict):
        return {__val_to_json_val(k): __val_to_json_val(x) for k, x in v.items()}
    if is_dataclass(v):
        return __data_class_to_dict(v)
    if _is_named_tuple_instance(v):
        return __named_tuple_to_dict(v)
    if isinstance(v, enum.Enum):
        return __val_to_json_val(v.value)
    raise NonJsonableValueError("Failed to convert %r to jsonable value", v)


def __json_val_to_t(v, t: TypeInspector):
    return t.convert(v)


def _get_args(t):
    return t.__args__


def _is_named_tuple_type(t):
    return issubclass(t, tuple) and hasattr(t, "_fields")


def _is_named_tuple_instance(o):
    return isinstance(o, tuple) and hasattr(o, "_fields")
