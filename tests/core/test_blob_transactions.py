import os
import pytest

from eth_utils import (
    ValidationError,
    to_bytes,
)
from hexbytes import (
    HexBytes,
)
from toolz import (
    merge,
)

from eth_account import (
    Account,
)
from eth_account.typed_transactions import (
    BlobTransaction,
)

TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "_test_data")
SIGNED_TX_PATH = os.path.join(TEST_DATA_PATH, "signed_tx.txt")
BLOB_DATA_1_PATH = os.path.join(TEST_DATA_PATH, "blob_data_1.txt")
BLOB_DATA_1_SIGNED_PATH = os.path.join(TEST_DATA_PATH, "blob_data_1_signed.txt")

TEST_ACCT = Account.from_key(
    "0x4646464646464646464646464646464646464646464646464646464646464646"
)

ZERO_BLOB = f"0x{'00' * 32 * 4096}"
ZERO_BLOB_VERSIONED_HASH = (
    "0x010657f37554c781402a22917dee2f75def7ab966d7b770905398eba3c444014"
)
ZERO_BLOB_COMMITMENT_AND_PROOF_HASH = "0xc00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"  # noqa: E501
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


def test_validation_when_blobs_are_present_with_incorrect_versioned_hashes_in_tx_dict():
    tx_dict_with_wrong_versioned_hashes = merge(
        BLOB_TX_DICT, {"blobVersionedHashes": [f"0x{'00' * 32}"]}
    )
    with pytest.raises(
        ValidationError,
        match=(
            "`blobVersionedHashes` value defined in transaction does not match "
            "versioned hashes computed from blobs."
        ),
    ):
        BlobTransaction.from_dict(
            tx_dict_with_wrong_versioned_hashes,
            blobs=[to_bytes(hexstr=ZERO_BLOB)],
        )


def test_blobs_commitments_proofs_and_hashes_from_blobs():
    # test that when correct blobVersionedHashes value is passed into tx dict,
    # validation does not raise
    correct_versioned_hashes = [ZERO_BLOB_VERSIONED_HASH]
    tx_dict_with_correct_versioned_hashes = merge(
        BLOB_TX_DICT, {"blobVersionedHashes": correct_versioned_hashes}
    )

    # test does not raise
    tx = BlobTransaction.from_dict(
        tx_dict_with_correct_versioned_hashes, blobs=[to_bytes(hexstr=ZERO_BLOB)]
    )
    assert (
        len(tx.blob_data.blobs)
        == len(tx.blob_data.versioned_hashes)
        == len(tx.blob_data.proofs)
        == 1
    )
    # assert calculated versioned hash is the same as the provided versioned hash
    assert tx.blob_data.versioned_hashes[0].as_hexstr() == ZERO_BLOB_VERSIONED_HASH

    assert (
        tx.blob_data.commitments[0].as_hexstr() == ZERO_BLOB_COMMITMENT_AND_PROOF_HASH
    )
    assert tx.blob_data.proofs[0].as_hexstr() == ZERO_BLOB_COMMITMENT_AND_PROOF_HASH


def test_sign_blob_transaction_with_zero_blob_and_compare_with_tx_from_bytes():
    # test case taken from web3j library:
    # https://github.com/web3j/web3j/blob/c0679c08dfc1e1b196d1086f47d2eedc72f2a8f7/crypto/src/test/resources/blob_data/blob_tx_signed.txt  # noqa: E501
    # https://github.com/web3j/web3j/blob/c0679c08dfc1e1b196d1086f47d2eedc72f2a8f7/crypto/src/test/java/org/web3j/crypto/TransactionEncoderTest.java#L123-L128  # noqa: E501
    with open(SIGNED_TX_PATH) as signed_tx_file:
        signed_tx_from_file = to_bytes(hexstr=signed_tx_file.read().strip("\n"))

    signed_tx = TEST_ACCT.sign_transaction(BLOB_TX_DICT, blobs=[ZERO_BLOB])
    assert signed_tx.raw_transaction == HexBytes(signed_tx_from_file)

    # test `from_bytes()` creates `blob_data`
    tx_from_bytes = BlobTransaction.from_bytes(HexBytes(signed_tx_from_file))
    assert tx_from_bytes.blob_data is not None
    assert (
        len(tx_from_bytes.blob_data.blobs)
        == len(tx_from_bytes.blob_data.versioned_hashes)
        == len(tx_from_bytes.blob_data.proofs)
        == 1
    )
    assert tx_from_bytes.blob_data.blobs[0].as_hexstr() == ZERO_BLOB
    assert (
        tx_from_bytes.blob_data.versioned_hashes[0].as_hexbytes()
        == (tx_from_bytes.dictionary["blobVersionedHashes"][0])
        == HexBytes(ZERO_BLOB_VERSIONED_HASH)
    )
    assert (
        tx_from_bytes.blob_data.commitments[0].as_hexstr()
        == ZERO_BLOB_COMMITMENT_AND_PROOF_HASH
    )
    assert (
        tx_from_bytes.blob_data.proofs[0].as_hexstr()
        == ZERO_BLOB_COMMITMENT_AND_PROOF_HASH
    )


def test_blob_transaction_calculation_with_nonzero_blob():
    # test case taken from web3j library:
    # https://github.com/web3j/web3j/blob/c0679c08dfc1e1b196d1086f47d2eedc72f2a8f7/crypto/src/test/resources/blob_data/blob_data_2.txt  # noqa: E501
    with open(BLOB_DATA_1_PATH) as blob_data_1_file:
        blob_data_1 = to_bytes(hexstr=blob_data_1_file.read().strip("\n"))

    tx = BlobTransaction.from_dict(BLOB_TX_DICT, blobs=[blob_data_1])
    assert (
        len(tx.blob_data.blobs)
        == len(tx.blob_data.versioned_hashes)
        == len(tx.blob_data.proofs)
        == 1
    )
    assert tx.blob_data.blobs[0].as_bytes() == blob_data_1
    assert tx.blob_data.versioned_hashes[0].as_hexstr() == (
        "0x018ef96865998238a5e1783b6cafbc1253235d636f15d318f1fb50ef6a5b8f6a"
    )
    assert tx.blob_data.proofs[0].as_hexstr() == (
        "0x963150f3ee4d5e5f065429f587b4fa199cd8a866b8f6388eb52372870052603c98194c6521077c3260c41bf3b796c833"  # noqa: E501
    )

    with open(BLOB_DATA_1_SIGNED_PATH) as blob_data_1_signed_file:
        blob_data_1_signed = to_bytes(hexstr=blob_data_1_signed_file.read().strip("\n"))

    signed = TEST_ACCT.sign_transaction(tx.dictionary, blobs=[blob_data_1])
    assert blob_data_1_signed == signed.raw_transaction


def test_high_and_low_blob_count_limit_validation():
    with pytest.raises(ValidationError, match="must contain at least 1 blob"):
        BlobTransaction.from_dict(BLOB_TX_DICT, blobs=[])

    # make sure up to 6 blobs can be added to a blob transaction
    BlobTransaction.from_dict(BLOB_TX_DICT, blobs=[to_bytes(hexstr=ZERO_BLOB)] * 6)

    # assert raises if more than 6 blobs
    with pytest.raises(ValidationError, match="cannot contain more than 6 blobs"):
        BlobTransaction.from_dict(BLOB_TX_DICT, blobs=[to_bytes(hexstr=ZERO_BLOB)] * 7)
