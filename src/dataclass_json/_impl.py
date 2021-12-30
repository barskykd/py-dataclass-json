import datetime
import enum
import inspect
from dataclasses import is_dataclass
from functools import lru_cache
# noinspection PyProtectedMember
from typing import Dict, _GenericAlias


class NonJsonableValueError(Exception):
    pass


class UndefinedType:
    def __bool__(self):
        return False


UNDEFINED = UndefinedType()  # Field with this value will be omitted from jsonable output


# noinspection PyProtectedMember
class TypeInspector:
    def __init__(self, t):
        self.__t = t
        self.is_none = self.__t is None
        self.is_int = self.__t is int
        self.is_float = self.__t is float
        self.is_bool = self.__t is bool
        self.is_str = self.__t is str
        self.is_datetime = self.__t is datetime.datetime
        self.is_dict = isinstance(self.__t, _GenericAlias) and self.__t._name == "Dict"
        self.is_list = isinstance(self.__t, _GenericAlias) and self.__t._name == "List"
        self.is_enum = is_enum(self.__t)
        self.is_dataclass = is_dataclass(self.__t)
        self.is_named_tuple = is_namedtuple(t)

    @property
    @lru_cache()
    def list_t(self):
        assert self.is_list
        return TypeInspector(self.__args()[0])

    @property
    @lru_cache()
    def dict_key_t(self):
        assert self.is_dict
        return TypeInspector(self.__args()[0])

    @property
    @lru_cache()
    def dict_val_t(self):
        assert self.is_dict
        return TypeInspector(self.__args()[1])

    def convert(self, v):
        if v is None:
            return None
        if self.is_datetime:
            return datetime.datetime.fromisoformat(v)
        if self.is_dataclass or self.is_named_tuple:
            return self.__t(**{k: t.convert(v[k]) for k, t in self.__ann().items() if k in v})
        if self.is_list:
            return [self.list_t.convert(x) for x in v]
        if self.is_dict:
            return {self.dict_key_t.convert(k): self.dict_val_t.convert(v) for k, v in v.items()}
        if self.is_enum:
            return self.__t(v)
        return v

    @lru_cache()
    def enum_values(self):
        assert self.is_enum
        return [x.value for x in self.__t]

    @lru_cache()
    def __ann(self) -> Dict[str, 'TypeInspector']:
        assert self.is_named_tuple or self.is_dataclass
        return {k: TypeInspector(v) for k, v in self.__t.__annotations__.items()}

    def __args(self):
        return self.__t.__args__

    def __gt__(self, other):
        return 0


def is_enum(t):
    try:
        return inspect.isclass(t) and issubclass(t, enum.Enum)
    except Exception as ex:
        raise Exception("Exception while checking whether %r is enum " % t) from ex


def is_namedtuple(t):
    return inspect.isclass(t) and issubclass(t, tuple) and hasattr(t, "_fields")
