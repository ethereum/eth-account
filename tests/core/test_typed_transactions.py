import pytest
from eth_account._utils.typed_transactions import (
    TypedTransaction,
)
from hexbytes import (
    HexBytes,
)

TEST_CASES = [
    {
        "expected_hash": '0x4f53cc08773081c51a1da2dc8df07b2e58cf8e359239efdb8dbf049be448974d',
        "expected_raw_transaction": "0x01f8ad82076c22843b9aca00830186a09409616c3d61b3331fc4109a9e41a8bdb7d9776609865af3107a400086616263646566f838f7940000000000000000000000000000000000000001e1a0010000000000000000000000000000000000000000000000000000000000000001a08289e85fa00f8f7f78a53cf147a87b2a7f0d27e64d7571f9d06a802e365c3430a017dc77eae36c88937db4a5179f57edc6119701652f3f1c6f194d1210d638a061",
        "transaction": {
            "gas":"0x186a0",
            "gasPrice":"0x3b9aca00",
            "data":"0x616263646566",
            "nonce":"0x22",
            "to":"0x09616C3d61b3331fc4109a9E41a8BDB7d9776609",
            "value":"0x5af3107a4000",
            "type":"0x1",
            "accessList":[
                [
                    "0x0000000000000000000000000000000000000001",
                    ["0x0100000000000000000000000000000000000000000000000000000000000000"],
                ],
            ],
            "chainId":"0x76c",
            "v":"0x1",
            "r":"0x8289e85fa00f8f7f78a53cf147a87b2a7f0d27e64d7571f9d06a802e365c3430",
            "s":"0x17dc77eae36c88937db4a5179f57edc6119701652f3f1c6f194d1210d638a061",
        }
    },
    {
        "expected_hash": "0x660fd2280b7ce4a6b625ccb2e1bb56fe3ede2ed91a7ff0b82a8d61e4709b82f6",
        "expected_raw_transaction": "0x01f87482076c27843b9aca00830186a09409616c3d61b3331fc4109a9e41a8bdb7d9776609865af3107a400086616263646566c080a0bad1a40fa2d90dc7539831bb82dfccf9b7094eab238d50c4369b805fb7241c58a046ab7eb7ff8cdfd203847b7e1b2f9e41208bba76a86ae3eeb97fe2727763aa12",
        "transaction": {
            "gas":"0x186a0",
            "gasPrice":"0x3b9aca00",
            "data":"0x616263646566",
            "nonce":"0x27",
            "to":"0x09616C3d61b3331fc4109a9E41a8BDB7d9776609",
            "value":"0x5af3107a4000",
            "type":"0x1",
            "accessList":[],
            "chainId":"0x76c",
            "v":"0x0",
            "r":"0xbad1a40fa2d90dc7539831bb82dfccf9b7094eab238d50c4369b805fb7241c58",
            "s":"0x46ab7eb7ff8cdfd203847b7e1b2f9e41208bba76a86ae3eeb97fe2727763aa12",
        },
    },
]

@pytest.mark.parametrize(
    'test_case',
    TEST_CASES,
    ids=['non-empty-list', 'empty-list'],
)
def test_hash(test_case):
    expected = test_case["expected_hash"]
    transaction = TypedTransaction.from_dict(test_case["transaction"])
    hash = transaction.hash()
    actual = HexBytes(hash).hex()
    assert actual == expected

@pytest.mark.parametrize(
    'test_case',
    TEST_CASES,
    ids=['non-empty-list', 'empty-list'],
)
def test_encode(test_case):
    expected = test_case["expected_raw_transaction"]
    transaction = TypedTransaction.from_dict(test_case["transaction"])
    raw_transaction = transaction.encode()
    actual = HexBytes(raw_transaction).hex()
    assert actual == expected    
