from pydantic import BaseModel

from fastapi import FastAPI
from typing import TypeVar
from servit import serve
app = FastAPI()

@serve(app)
class MyData(BaseModel):
    name: str

    @staticmethod
    def get(name: str) -> 'MyData':
        """Get a data model"""
        return MyData(name=name)


    def get_name(self, start: int = 3):
        return self.name[start:]

