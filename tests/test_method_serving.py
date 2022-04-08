import pytest
import json
from fastapi.testclient import TestClient

from pydantic import BaseModel
from fastapi import FastAPI
from servit import serve

app = FastAPI()


@serve(app)
class Class(BaseModel):
    name: str

    @staticmethod
    def get(
        name: str,
    ):  #  -> "Class": # https://github.com/tiangolo/fastapi/issues/4557
        """Get a data model"""
        return Class(name=name)

    def get_name(self, start: int = 3) -> str:
        return self.name[start:]


@pytest.fixture
def client():
    return TestClient(app)


def test_only_post_allowed(client):
    assert client.get("class/get?name=hello").status_code == 405
    assert client.put("class/get?name=hello").status_code == 405
    assert client.delete("class/get?name=hello").status_code == 405


def test_static_method(client):
    assert client.post("class/get?name=hello").json() == {"name": "hello"}


def test_default_param(client):
    res = client.post("class/get_name", json={"name": "Hello world"})
    assert res.json() == {"value": "lo world"}


def test_non_default_param(client):
    res = client.post("class/get_name?start=0", json={"name": "Hello world"})
    assert res.json() == {"value": "Hello world"}


# TODO: Error cases (idx out of bounds, bad index, etc.. see that error messages are fine
