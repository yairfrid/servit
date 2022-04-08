from servit import serve, InMemoryObjectStore
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.testclient import TestClient
import pytest


app = FastAPI()


@serve(app, store=InMemoryObjectStore)
class Class(BaseModel):
    st: str

    @staticmethod
    def get(st: str):  #  -> "Class":
        return Class(st=st)

    def get_st(self) -> str:
        return self.st


@pytest.fixture
def client():

    # Test case for Class # TODO: Move this from fixture..
    assert getattr(Class, "_servit_obj_store", None) is not None

    return TestClient(app)


# TODO: Further testing
def test_object_store(client):
    res = client.post("class/get?st=test_str")
    json = res.json()
    assert list(json.keys()) == ["id"]
    assert isinstance(json["id"], str)
    id = json["id"]
    assert client.post(f"class/{id}/get_st").json() == {"value": "test_str"}
