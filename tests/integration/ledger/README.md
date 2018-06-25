To run the test a ledger device must be connected and the Ethereum application running on it.

Install ledger requirement: 
```sh
# in the project root:
pip install -e .[ledger]
```

Run the tests with:
```sh
# in the project root:
pytest tests/integration/ledger/test_ledger.py
```
