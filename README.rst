To run tests:
first, start the server with `uvicorn --factory --reload tests.<TEST_FILE>:server`

Then, to trigger the test, run `python tests/<TEST_FILE>`

Known issues:

Can't use postponed annotations: https://github.com/tiangolo/fastapi/issues/4557

TODO:  

[ * ] Convert tests to pytest

[ * ] Object store support

[ ] Write a shit load of tests and clean up code

[ ] add full path (directory path and file name) before class name when publishing an endpoint, so we can structure the server using python packages

[ ] Create a test for swagger documentation

[ ] Documentation  

[ ] Type hints

