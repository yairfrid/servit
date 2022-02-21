def server():
    from servit import serve, InMemoryObjectStore
    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI()

    @serve(app, store=InMemoryObjectStore)
    class TestClass(BaseModel):
        st: str

        @staticmethod
        def get(st: str) -> "TestClass":
            return TestClass(st=st)

    # Test case for TestClass
    assert getattr(TestClass, "_servit_obj_store", None) is not None

    return app


def client():
    import requests

    res = requests.post("http://localhost:8000/test_class/get?st=test_str")
    json = res.json()
    assert list(json.keys()) == ["_id"]
    assert isinstance(json["_id"], str)


if __name__ == "__main__":
    client()
