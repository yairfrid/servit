import inspect
import functools
from types import FunctionType
import itertools
from typing import Type, Optional, get_type_hints
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from .object_store import ObjectStore


def get_methods(cls):
    return set(
        [
            val
            for key, val in cls.__dict__.items()
            if not key.startswith("_") and callable(val)
        ]
    )


def get_method_name(method):
    return method.__name__


def get_method_names(cls):
    return [get_method_name(method) for method in get_methods(cls)]


def get_parent_methods(cls):
    parents = cls.__mro__[1:]
    return set(itertools.chain(*[get_methods(parent) for parent in parents]))


def camel_to_snake(st):
    st = st[:1].lower() + st[1:]
    ret = []
    for c in st[1:]:
        if c.lower() == c:
            ret.append(c)
        else:
            ret.append("_")
            ret.append(c.lower())
    return st[0].lower() + "".join(ret)


def get_return_type(func) -> Optional[str]:
    ret = inspect.signature(func).return_annotation
    return str(ret) if ret else None


def decorate_method(method, cls):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):

        ret_value = method(*args, **kwargs)
        if get_return_type(method) != cls.__name__:
            ret_value = JSONResponse(content={"value": ret_value})
        return ret_value

    return wrapper


def serve(app, *, store: Optional[Type[ObjectStore]] = None):
    def inner(cls):
        if not issubclass(cls, BaseModel):
            raise TypeError("Only pydantic BaseModels can be served")

        if store is not None:
            instance = store(typ=cls)
            setattr(cls, "_servit_obj_store", instance)
        methods = get_methods(cls) - get_parent_methods(cls)
        for method in methods:
            if isinstance(method, classmethod):
                raise ValueError("Class methods not yet supported")
            elif isinstance(
                method, staticmethod
            ):  # TODO: There should probably be a better way to determine if method is an instance method or not
                method = method.__func__
            else:
                method.__annotations__ |= {
                    "self": cls
                }  # TODO: This should work on the first arg and not 'self' as self is not guranteed

            method_name = get_method_name(method)

            method = decorate_method(method, cls)

            app.post(f"/{camel_to_snake(cls.__name__)}/{method_name}")(method)
        return cls

    return inner
