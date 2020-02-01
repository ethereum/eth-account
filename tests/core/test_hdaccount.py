from eth_account import (
    Account,
)


# https://github.com/MetaMask/eth-hd-keyring/blob/master/test/index.js
def test_account_derivation():
    words = "finish oppose decorate face calm tragic certain desk hour urge dinosaur mango"
    a1 = Account.from_mnemonic(words)
    a2 = Account.from_mnemonic(words, account_index=1)
    assert a1.address == "0x1c96099350f13D558464eC79B9bE4445AA0eF579"
    assert a2.address == "0x1b00AeD43a693F3a957F9FeB5cC08AFA031E37a0"
