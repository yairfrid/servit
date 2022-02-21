import inspect
import functools
from types import FunctionType
import itertools
from typing import Type

from .object_store import ObjectStore


def get_methods(cls):

    return set([
        val
        for key, val in cls.__dict__.items()
        if not key.startswith("_") and callable(val)
    ])


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


def serve(app, object_store: Type[ObjectStore] = None):
    def inner(cls):
        methods = get_methods(cls) - get_parent_methods(cls)
        for method in methods:
            if isinstance(method, classmethod):
                raise ValueError("Class methods not yet supported")
            elif isinstance(method, staticmethod):
                method = method.__func__
            else:
                method.__annotations__ |= {"self": cls}
            method_name = get_method_name(method)
            app.post(f"/{camel_to_snake(cls.__name__)}/{method_name}")(method)
        return cls

    return inner
