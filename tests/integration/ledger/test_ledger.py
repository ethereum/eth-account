# Require a connected Ledger ...

import pytest

from hexbytes import (
    HexBytes,
)

from eth_account import (
    Account,
)
from eth_account.messages import (
    defunct_hash_message,
)
from eth_account.signers.ledger import (
    LedgerAccount,
)

# Not a fixture because it does not support multiple LedgerAccount
ledger = LedgerAccount()


@pytest.fixture
def acct(request):
    return Account


@pytest.fixture
def ledger_invalid():
    return LedgerAccount(address='0x0000000000000000000000000000000000000000')


@pytest.fixture
def transaction():
    return {
        'to': '0x0000000000000000000000000000000000000000',
        'value': 0,
        'gas': 2000000,
        'gasPrice': 65536,
        'nonce': 0,
        'chainId': 1
    }


@pytest.fixture
def tx_hash():
    return HexBytes('0xdd4998746632108893ed905116ec4c1839833f6f3c9ae276b6550e15bad308c8')


def test_address():
    address = ledger.address
    account_id = ledger.get_account_id(address)

    assert address == ledger.get_address(account_id)


def test_get_addresses():
    accounts_1 = ledger.get_addresses(1)
    assert len(accounts_1) == 1

    accounts_5 = ledger.get_addresses(5)
    assert len(accounts_5) == 5
    assert accounts_1[0] == accounts_5[0]

    accounts_10 = ledger.get_addresses(10)
    assert len(accounts_10) == 10
    assert accounts_5 == accounts_10[:5]

    accounts_4p0 = ledger.get_addresses(limit=4, page=0)
    accounts_4p1 = ledger.get_addresses(limit=4, page=1)
    accounts_4p2 = ledger.get_addresses(limit=4, page=2)
    assert len(accounts_4p1) == 4
    assert accounts_4p0 == accounts_10[:4]
    assert accounts_4p1 == accounts_10[4:8]
    assert accounts_10 == (accounts_4p0 + accounts_4p1 + accounts_4p2[:2])


def test_sign_transaction(transaction, tx_hash, acct):
    expected_sender = ledger.address
    signed = ledger.signTransaction(transaction)

    assert type(signed.v) is int
    assert type(signed.r) is str
    assert type(signed.s) is str

    assert signed.hash == tx_hash

    assert acct.recoverTransaction(signed.rawTransaction).lower() == expected_sender

    # Test transaction with a small payload
    transaction['data'] = bytes([0x0] * 128)
    signed = ledger.signTransaction(transaction)
    assert acct.recoverTransaction(signed.rawTransaction).lower() == expected_sender

    # Test transaction with a large payload
    transaction['data'] = bytes([0x0] * 1042)
    signed = ledger.signTransaction(transaction)
    assert acct.recoverTransaction(signed.rawTransaction).lower() == expected_sender


def test_defunct_sign_message(acct):
    message = "I♥SF"
    msghash = defunct_hash_message(text=message)

    expected_signer = ledger.address

    signed = ledger.defunctSignMessage(text=message)

    assert signed.messageHash == msghash
    assert type(signed.v) is int
    assert type(signed.r) is str
    assert type(signed.s) is str

    vrs = (signed.v, signed.r, signed.s)
    from_account = acct.recoverHash(signed.messageHash, vrs=vrs)
    assert from_account.lower() == expected_signer
