To run tests:
first, start the server with `uvicorn --factory --reload tests.<TEST_FILE>:server`

Then, to trigger the test, run `python tests/<TEST_FILE>`


TODO:
[ ] Convert tests to pytest, run the server async in a fixture
[ ] add full path (directory path and file name) before class name when publishing an endpoint, so we can structure the server using python packages
[ ] Create a test for swagger documentation
