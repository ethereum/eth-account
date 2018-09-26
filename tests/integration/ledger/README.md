To run the test a ledger device must be connected and the Ethereum application running on it.

The following seed must be used to initilalize the ledger. Without it the tests
would fail on addresses, hash and signature assertion.
```
later galaxy arrange short length wisdom
impact balcony vague coast lunch promote
dust save enroll gain wreck welcome
rotate elder abandon grain master eager
```

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
