import pytest

from eth_utils import (
    ValidationError,
)

from eth_account import (
    Account,
)
from eth_account.hdaccount import (
    ETHEREUM_DEFAULT_PATH,
)

Account.enable_unaudited_hdwallet_features()


@pytest.mark.parametrize(
    "mnemonic,account_path,expected_address",
    [
        # Ganache
        # https://github.com/trufflesuite/ganache-core/blob/d1cb5318cb3c694743f86f29d74/test/accounts.js
        (
            "into trim cross then helmet popular suit hammer cart shrug oval student",
            ETHEREUM_DEFAULT_PATH,
            "0x604a95C9165Bc95aE016a5299dd7d400dDDBEa9A",
        ),
        # Metamask
        # https://github.com/MetaMask/eth-hd-keyring/blob/79d088e4a73624537e924b3943830526/test/index.js
        (
            "finish oppose decorate face calm tragic certain desk hour urge dinosaur mango",  # noqa: E501
            ETHEREUM_DEFAULT_PATH,
            "0x1c96099350f13D558464eC79B9bE4445AA0eF579",
        ),
        (
            "finish oppose decorate face calm tragic certain desk hour urge dinosaur mango",  # noqa: E501
            "m/44'/60'/0'/0/1",  # 2nd account index in path
            "0x1b00AeD43a693F3a957F9FeB5cC08AFA031E37a0",
        ),
    ],
)
def test_account_derivation(mnemonic, account_path, expected_address):
    a = Account.from_mnemonic(mnemonic, account_path=account_path)
    assert a.address == expected_address


def test_account_restore():
    a1, mnemonic = Account.create_with_mnemonic(num_words=24, passphrase="TESTING")
    a2 = Account.from_mnemonic(mnemonic, passphrase="TESTING")
    assert a1.address == a2.address


def test_bad_passphrase():
    a1, mnemonic = Account.create_with_mnemonic(passphrase="My passphrase")
    a2 = Account.from_mnemonic(mnemonic, passphrase="Not my passphrase")
    assert a1.address != a2.address


def test_incorrect_size():
    with pytest.raises(ValidationError, match="Language not detected .*"):
        Account.from_mnemonic("this is not a seed phrase")


def test_malformed_seed():
    with pytest.raises(ValidationError, match=".* not a valid BIP39 mnemonic phrase!"):
        # Missing 12th word
        Account.from_mnemonic(
            "into trim cross then helmet popular suit hammer cart shrug oval"
        )


def test_incorrect_checksum():
    with pytest.raises(ValidationError, match=".* not a valid BIP39 mnemonic phrase!"):
        # Moved 12th word of valid phrase to be 1st
        Account.from_mnemonic(
            "student into trim cross then helmet popular suit hammer cart shrug oval"
        )


def test_incorrect_num_words():
    with pytest.raises(ValidationError, match="Invalid choice for number of words.*"):
        Account.create_with_mnemonic(num_words=11)


def test_bad_account_path1():
    with pytest.raises(ValidationError, match="Path is not valid.*"):
        Account.from_mnemonic(
            "finish oppose decorate face calm tragic certain desk hour urge dinosaur mango",  # noqa: E501
            account_path="not an account path",
        )


def test_bad_account_path2():
    with pytest.raises(ValidationError, match="Path.*is not valid.*"):
        Account.create_with_mnemonic(account_path="m/not/an/account/path")


def test_unknown_language():
    with pytest.raises(ValidationError, match="Invalid language choice.*"):
        Account.create_with_mnemonic(language="pig latin")
