import inspect
import functools
import types
from types import FunctionType
import itertools
from typing import Type, Optional, get_type_hints, Callable, Type, Set, List, TypeVar
from fastapi.responses import JSONResponse

from pydantic import BaseModel, create_model

from .object_store import ObjectStore, IdModel

JSON_PRIMITIVE_TYPES = ["str", "int", "float", "list", "dict"]




def get_methods(cls: Type[BaseModel]) -> Set[Callable]:
    return set(
        [
            val
            for key, val in cls.__dict__.items()
            if not key.startswith("_") and callable(val)
        ]
    )


def get_method_name(method: Callable) -> str:
    return method.__name__


def get_method_names(cls: Type[BaseModel]) -> List[str]:
    return [get_method_name(method) for method in get_methods(cls)]


def get_parent_methods(cls: Type[BaseModel]) -> Set[Callable]:
    parents = cls.__mro__[1:]
    return set(itertools.chain(*[get_methods(parent) for parent in parents]))


def camel_to_snake(st: str) -> str:
    st = st[:1].lower() + st[1:]
    ret = []
    for c in st[1:]:
        if c.lower() == c:
            ret.append(c)
        else:
            ret.append("_")
            ret.append(c.lower())
    return st[0].lower() + "".join(ret)


def snake_to_camel(st: str) -> str:
    return "".join([sub.capitalize() for sub in st.split("_")])


def get_return_type_name(func: Callable) -> Optional[str]:
    ret = inspect.signature(func).return_annotation
    return ret.__name__ if ret is not inspect.Parameter.empty else None


def get_return_type(func: Callable) -> Type:
    return inspect.signature(func).return_annotation


def replace_arg_name(f: Callable, pre: str, post: str) -> Callable:
    """

    change parameter 'pre' of f to be named 'post'
    """
    code_obj = f.__code__
    new_varnames = tuple(var if var != pre else post for var in code_obj.co_varnames)
    new_code_obj = types.CodeType(
        code_obj.co_argcount,
        code_obj.co_posonlyargcount,
        code_obj.co_kwonlyargcount,
        code_obj.co_nlocals,
        code_obj.co_stacksize,
        code_obj.co_flags,
        code_obj.co_code,
        code_obj.co_consts,
        code_obj.co_names,
        new_varnames,
        code_obj.co_filename,
        code_obj.co_name,
        code_obj.co_firstlineno,
        code_obj.co_lnotab,
    )

    modified = types.FunctionType(new_code_obj, f.__globals__)
    annotations = f.__annotations__.copy()
    if pre in annotations:
        annotation = annotations[pre]
        del annotations[pre]
        annotations[post] = annotation
    modified.__annotations__ = annotations
    return modified


def decorate_method_input(method: Callable, cls: Type) -> Callable:
    obj_store = getattr(cls, "_servit_obj_store", None)

    if not obj_store:
        return method

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        if 'id' in kwargs:
            self = obj_store.get(kwargs['id'])
            kwargs.pop('id')
            breakpoint
            return method(self, *args, **kwargs)
        else:
            return method(*args, **kwargs)

    return wrapper

def decorate_method_output(method: Callable, cls: Type) -> Callable:
    obj_store = getattr(cls, "_servit_obj_store", None)

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        ret_value = method(*args, **kwargs)
        # TODO: What to do if return type is not a json type?
        print(get_return_type_name(method))
        if get_return_type_name(method) == "IdModel":
            ret_value = IdModel(id=obj_store.set(ret_value))
        elif get_return_type_name(method) in JSON_PRIMITIVE_TYPES:
            ret_value = JSONResponse({"value": ret_value})

        print(ret_value)
        return ret_value

    if obj_store is not None and get_return_type_name(method) == cls.__name__:
        wrapper.__annotations__["return"] = IdModel

    return wrapper


def serve(app, *, store: Optional[Type[ObjectStore]] = None) -> Callable:
    def inner(cls: Type[BaseModel]) -> Type[BaseModel]:
        if not issubclass(cls, BaseModel):
            raise TypeError("Only pydantic BaseModels can be served")

        if store is not None:
            instance = store(typ=cls)
            setattr(cls, "_servit_obj_store", instance)
        methods = get_methods(cls) - get_parent_methods(cls)
        for method in methods:

            id_endpoint_part = ""
            if isinstance(method, classmethod):
                raise ValueError("Class methods not yet supported")
            elif isinstance(
                method, staticmethod
            ):  # TODO: There should probably be a better way to determine if method is an instance method or not
                method = method.__func__
            else:
                sig = inspect.signature(method)
                # Name of first argument or _id
                first_param_name = list(sig.parameters.items())[0][1].name

                if store:
                    id_endpoint_part = "/{id}"
                    method = replace_arg_name(method, first_param_name, "id")
                elif first_param_name not in method.__annotations__:
                    method.__annotations__[first_param_name] = cls

            method_name = get_method_name(method)

            return_type_name = get_return_type_name(method)
            if return_type_name is None:
                print(
                    f"WARNING: No return type was specified, so {cls.__name__} was inferred"
                )
                return_type = cls
                if store:
                    return_type = IdModel
                method.__annotations__['return'] = return_type
            elif return_type_name in JSON_PRIMITIVE_TYPES:
                return_type = create_model(
                    snake_to_camel(method_name) + "Model",
                    value=(get_return_type(method), ...),
                )
            else:
                return_type = get_return_type(method)

            method = decorate_method_input(method, cls)
            method = decorate_method_output(method, cls)

            endpoint = (
                f"/{camel_to_snake(cls.__name__)}{id_endpoint_part}/{method_name}"
            )
            app.post(endpoint, response_model=return_type)(method)
        return cls

    return inner
