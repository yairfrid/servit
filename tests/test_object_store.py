from servit import serve, InMemoryObjectStore
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.testclient import TestClient
import pytest

@pytest.fixture
def client():

    app = FastAPI()

    @serve(app, store=InMemoryObjectStore)
    class TestClass(BaseModel):
        st: str

        @staticmethod
        def get(st: str) -> "TestClass":
            return TestClass(st=st)

    # Test case for TestClass # TODO: Move this from fixture..
    assert getattr(TestClass, "_servit_obj_store", None) is not None

    return TestClient(app)

# TODO: Further testing
def test_object_store(client):
    res = client.post("test_class/get?st=test_str")
    json = res.json()
    assert list(json.keys()) == ["_id"]
    assert isinstance(json["_id"], str)

