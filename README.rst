To run tests:
first, start the server with `uvicorn --factory --reload tests.<TEST_FILE>:server`

Then, to trigger the test, run `python tests/<TEST_FILE>`


TODO:
[ ] Create a test runner (a script that goes over all of the tests and runs them like in the description above, also redo the description afterwards and add a poetry task so `poetry test` works as expected
[ ] Create a test for documentation
