from typing import Generic, TypeVar
from abc import ABC, abstractmethod

ObjType = TypeVar('ObjType')

class ObjectStore(ABC, Generic[ObjType]):
    typ: ObjType

    def __init__(self, typ: ObjType):
        self.typ = typ

    @abstractmethod
    def set(obj: ObjType) -> str:
        pass

    def get(_id: str) -> ObjType:
        pass

        
class InMemoryObjectStore(ObjectStore):

    def __init__(self, typ: ObjType):
        super().__init__(self, typ)
        self.map = {}

    def set(obj: ObjType) -> str:
        self.map |= {id(obj): obj}
        return id(obj)

    def get(_id: str) -> ObjType:
        return self.map[_id]
