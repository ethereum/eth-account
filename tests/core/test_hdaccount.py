import pytest

from eth_account import (
    Account,
)
from eth_utils import (
    ValidationError,
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
    a1, mnemonic = Account.create_with_mnemonic(num_words=24, passphrase="TESTING")
    a2 = Account.from_mnemonic(mnemonic, passphrase="TESTING")
    assert a1.address == a2.address


def test_incorrect_size():
    with pytest.raises(ValidationError):
        Account.from_mnemonic("this is not a seed phrase")


def test_malformed_seed():
    with pytest.raises(ValidationError):
        # Missing 12th word
        Account.from_mnemonic("into trim cross then helmet popular suit hammer cart shrug oval")


def test_incorrect_checksum():
    with pytest.raises(ValidationError):
        # Moved 12th word of valid phrase to be 1st
        Account.from_mnemonic(
            "student into trim cross then helmet popular suit hammer cart shrug oval"
        )
