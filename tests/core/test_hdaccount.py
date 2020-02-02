import pytest

from eth_account import (
    Account,
)


@pytest.mark.parametrize("mnemonic,expected_addresses", [
    (
        # Metamask
        # https://github.com/MetaMask/eth-hd-keyring/blob/master/test/index.js
        "finish oppose decorate face calm tragic certain desk hour urge dinosaur mango",
        [
            "0x1c96099350f13D558464eC79B9bE4445AA0eF579",
            "0x1b00AeD43a693F3a957F9FeB5cC08AFA031E37a0",
        ],
    ),
    (
        # Ganache
        # https://github.com/trufflesuite/ganache-core/blob/master/test/accounts.js
        "into trim cross then helmet popular suit hammer cart shrug oval student",
        [
            "0x604a95C9165Bc95aE016a5299dd7d400dDDBEa9A",
        ],
    ),
])
def test_account_derivation(mnemonic, expected_addresses):
    for idx, addr in enumerate(expected_addresses):
        a = Account.from_mnemonic(mnemonic, account_index=idx)
        assert a.address == addr


def test_account_restore():
    a1, mnemonic = Account.create_with_mnemonic(extra_entropy="Some extra stuff.")
    a2 = Account.from_mnemonic(mnemonic)
    assert a1.address == a2.address
