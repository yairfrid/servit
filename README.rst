To run tests:
first, start the server with `uvicorn --factory --reload tests.<TEST_FILE>:server`

Then, to trigger the test, run `python tests/<TEST_FILE>`

Known issues:

Can't use postponed annotations: https://github.com/tiangolo/fastapi/issues/4557

TODO:  

[ * ] Convert tests to pytest

[ * ] Object store support

[ ] Write a shit load of tests and clean up code

[ ] Create a test for swagger documentation

[ ] Documentation  

[ * ] Type hints

[ ] Examples:
  [ ] TODO app? (Basic Crud InMemory)
  [ ] Math Expression calculator (With no Memory)
  [ ] Portfolio manager (with Mongo?)

