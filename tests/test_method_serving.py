def server():
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

    return app


def client():
    import requests
    import json

    url = "http://localhost:8000/test_class"

    get_res = requests.post(f"{url}/get?name=hello")

    get_res.raise_for_status()
    assert get_res.json() == {"name": "hello"}

    get_name_no_param_res = requests.post(
        f"{url}/get_name", data=json.dumps({"name": "Hello world"})
    )
    get_name_no_param_res.raise_for_status()
    get_name_no_param_res.json() == {"name": "lo world"}

    get_name_param_res = requests.post(
        f"{url}/get_name?start=0", data=json.dumps({"name": "Hello world"})
    )
    get_name_param_res.raise_for_status()
    get_name_param_res.json() == {"name": "Hello world"}

    # TODO: Error cases (idx out of bounds, bad index, etc.. see that error messages are fine


if __name__ == "__main__":
    client()
