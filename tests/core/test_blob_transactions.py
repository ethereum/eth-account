import os

from eth_utils import (
    to_bytes,
)
from hexbytes import (
    HexBytes,
)

from eth_account import (
    Account,
)

SIGNED_TX_PATH = os.path.join(os.path.dirname(__file__), "_test_data", "signed_tx.txt")
TEST_ACCT = Account.from_key(
    "0x4646464646464646464646464646464646464646464646464646464646464646"
)
ZERO_BLOB = f"0x{'00' * 32 * 4096}"
BLOB_TX_DICT = {
    "chainId": 1,
    "nonce": 1,
    "maxPriorityFeePerGas": 50,
    "maxFeePerGas": 1000,
    "gas": 100000,
    "to": "0x45Ae5777c9b35Eb16280e423b0d7c91C06C66B58",
    "value": 1,
    "data": "0x52fdfc072182654f",
    "maxFeePerBlobGas": 100,
}


def test_sign_blob_pooled_transaction_from_dict_with_zero_blob():
    # test case taken from web3j library:
    # https://github.com/web3j/web3j/blob/c0679c08dfc1e1b196d1086f47d2eedc72f2a8f7/crypto/src/test/resources/blob_data/blob_tx_signed.txt  # noqa: E501
    # https://github.com/web3j/web3j/blob/c0679c08dfc1e1b196d1086f47d2eedc72f2a8f7/crypto/src/test/java/org/web3j/crypto/TransactionEncoderTest.java#L123-L128  # noqa: E501
    with open(SIGNED_TX_PATH) as signed_tx_file:
        signed_tx_from_file = to_bytes(hexstr=signed_tx_file.read().strip("\n"))
        signed_tx = TEST_ACCT.sign_transaction(BLOB_TX_DICT, blobs=[ZERO_BLOB])
        assert signed_tx.rawTransaction == HexBytes(signed_tx_from_file)
