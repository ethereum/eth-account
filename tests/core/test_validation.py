import pytest

from cytoolz import (
    dissoc,
)

from eth_account import (
    Account,
)

GOOD_TXN = {
    'chainId': 1,
    'gasPrice': 2,
    'gas': 200000,
    'nonce': 3,
}


@pytest.mark.parametrize(
    'txn_dict, bad_fields',
    (
        (dict(GOOD_TXN), {}),
        (dict(GOOD_TXN, to=None), {}),
        (dict(GOOD_TXN, to=b''), {}),
        (dict(GOOD_TXN, to=b'\0' * 20), {}),
        (dict(GOOD_TXN, to=b'\0' * 19), {'to'}),
        (dict(GOOD_TXN, to=b'\0' * 21), {'to'}),
        (dict(GOOD_TXN, to='0x' + '00' * 20), {}),
        pytest.mark.xfail(reason="eth-utils accepts 19-byte hex address as address")(
            (dict(GOOD_TXN, to='0x' + '00' * 19), {'to'})
        ),
        (dict(GOOD_TXN, to='0x' + '00' * 21), {'to'}),
        (dict(GOOD_TXN, gas='0e1'), {'gas'}),
        (dict(GOOD_TXN, gasPrice='0e1'), {'gasPrice'}),
        (dict(GOOD_TXN, value='0e1'), {'value'}),
        (dict(GOOD_TXN, nonce='0e1'), {'nonce'}),
        (dict(GOOD_TXN, gas='0b1'), {'gas'}),
        (dict(GOOD_TXN, gasPrice='0b1'), {'gasPrice'}),
        (dict(GOOD_TXN, value='0b1'), {'value'}),
        (dict(GOOD_TXN, nonce='0b1'), {'nonce'}),
        (dict(GOOD_TXN, chainId=None), {}),
        (dict(GOOD_TXN, chainId='0x1'), {}),
        (dict(GOOD_TXN, chainId='1'), {'chainId'}),

        # superfluous keys will be rejected (note the lower case p)
        (dict(GOOD_TXN, gasprice=1), {'gasprice'}),

        # missing keys will be called out explicitly
        (dissoc(GOOD_TXN, 'chainId'), {'chainId'}),
        (dissoc(GOOD_TXN, 'gasPrice'), {'gasPrice'}),
        (dissoc(GOOD_TXN, 'gas'), {'gas'}),
        (dissoc(GOOD_TXN, 'nonce'), {'nonce'}),
    ),
)
def test_invalid_transaction_fields(txn_dict, bad_fields):
    if not bad_fields:
        Account.signTransaction(txn_dict, b'\0' * 32)
    else:
        with pytest.raises(TypeError) as excinfo:
            Account.signTransaction(txn_dict, b'\0' * 32)
        for field in bad_fields:
            assert field in str(excinfo.value)
