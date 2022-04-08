from typing import Generic, TypeVar
from abc import ABC, abstractmethod
from pydantic import BaseModel

ObjType = TypeVar("ObjType")


class IdModel(BaseModel):
    id: str


class ObjectStore(ABC, Generic[ObjType]):
    typ: ObjType

    def __init__(self, typ: ObjType):
        self.typ = typ

    @abstractmethod
    def set(self, obj: ObjType) -> str:
        pass

    def get(self, _id: str) -> ObjType:
        pass


class InMemoryObjectStore(ObjectStore):
    def __init__(self, typ: ObjType):
        super().__init__(typ)
        self.map = {}

    def set(self, obj: ObjType) -> str:
        self.map |= {str(id(obj)): obj}
        return str(id(obj))

    def get(self, _id: str) -> ObjType:
        return self.map[_id]
