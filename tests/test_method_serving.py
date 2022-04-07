import pytest
import json
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from pydantic import BaseModel
    from fastapi import FastAPI
    from servit import serve

    app = FastAPI()

    @serve(app)
    class TestClass(BaseModel):
        name: str

        @staticmethod
        def get(name: str) -> "TestClass":
            """Get a data model"""
            return TestClass(name=name)

        def get_name(self, start: int = 3):
            return self.name[start:]

    return TestClient(app)


def test_only_post_allowed(client):
    assert client.get("test_class/get?name=hello").status_code == 405
    assert client.put("test_class/get?name=hello").status_code == 405
    assert client.delete("test_class/get?name=hello").status_code == 405


def test_static_method(client):
    assert client.post("test_class/get?name=hello").json() == {"name": "hello"}


def test_default_param(client):
    res = client.post("test_class/get_name", json={"name": "Hello world"})
    assert res.json() == {"value": "lo world"}


def test_non_default_param(client):
    res = client.post("test_class/get_name?start=0", json={"name": "Hello world"})
    assert res.json() == {"value": "Hello world"}


# TODO: Error cases (idx out of bounds, bad index, etc.. see that error messages are fine
