from eth_utils.exceptions import (
    ValidationError,
)
import pytest

from eth_account.messages import (
    _hash_eip191_message,
    encode_structured_data,
)

"""
`encode_structured_data` is eth-account's take on EIP-712 typed structured data hashing.

signTypedData is MetaMask's interpretation:
https://github.com/MetaMask/eth-sig-util/tree/main

Their signTypedData_v4 has become a de facto standard.

There is no clarification in the EIP about how to handle missing or extra data.
signTypedData_v4 has taken a more permissive approach than eth-account has.

The tests below will clarify what encode_structured_data allows.
The table and tests borrow heavily from `eth-sig-util`'s:
https://github.com/MetaMask/eth-sig-util/blob/main/src/sign-typed-data.test.ts


| Input type                                   | encode_structured_data |
| -------------------------------------------- | ---------------------- |
| Example data from EIP-712                    | Y                      |
| Example data from EIP-712 w/ array           | Y                      |
| Custom type                                  | Y                      |
| Recursive custom type                        | Y                      |
| Unused custom type                           | Y*                     |
| Custom type w/ extra properties in `message` | Y*                     |
| Custom type w/ extra properties in `types`   | N                      |
| Atomic type w/ `None` input                  | N                      |
| Atomic type missing                          | N                      |
| Dynamic type w/ `None` input                 | N                      |
| Dynamic type missing                         | N                      |
| Custom type w/ `None` input                  | N                      |
| Custom type missing                          | N                      |
| Unrecognized primary type                    | N                      |

* encode_structured_data ignores fields in `message` and `domain` that are not in
`types`, and same for custom types defined in `types` that are not present in `message`.
A message containing such fields will hash, but the output will be the same as with
those fields removed.
"""


@pytest.mark.parametrize(
    "_input_type, expected_esd_hash, message_to_encode",
    (
        (
            "Example data from EIP-712",
            "be609aee343fb3c4b28e1df9e632fca64fcfaede20f02e86244efddf30957bd2",
            {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                        {"name": "version", "type": "string"},
                        {"name": "chainId", "type": "uint256"},
                        {"name": "verifyingContract", "type": "address"},
                    ],
                    "Person": [
                        {"name": "name", "type": "string"},
                        {"name": "wallet", "type": "address"},
                    ],
                    "Mail": [
                        {"name": "from", "type": "Person"},
                        {"name": "to", "type": "Person"},
                        {"name": "contents", "type": "string"},
                    ],
                },
                "primaryType": "Mail",
                "domain": {
                    "name": "Ether Mail",
                    "version": "1",
                    "chainId": 1,
                    "verifyingContract": "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC",
                },
                "message": {
                    "from": {
                        "name": "Cow",
                        "wallet": "0xCD2a3d9F938E13CD947Ec05AbC7FE734Df8DD826",
                    },
                    "to": {
                        "name": "Bob",
                        "wallet": "0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB",
                    },
                    "contents": "Hello, Bob!",
                },
            },
        ),
        (
            "Example data from EIP-712 with array",
            "1780e7e042fa9ec126ccb68cd707d61580d00601b3eff8a5ec05116b46007fdb",
            {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                        {"name": "version", "type": "string"},
                        {"name": "chainId", "type": "uint256"},
                        {"name": "verifyingContract", "type": "address"},
                    ],
                    "Person": [
                        {"name": "name", "type": "string"},
                        {"name": "wallet", "type": "address"},
                    ],
                    "Mail": [
                        {"name": "from", "type": "Person"},
                        {"name": "to", "type": "Person"},
                        {"name": "cc", "type": "Person[]"},
                        {"name": "contents", "type": "string"},
                    ],
                },
                "primaryType": "Mail",
                "domain": {
                    "name": "Ether Mail",
                    "version": "1",
                    "chainId": 1,
                    "verifyingContract": "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC",
                },
                "message": {
                    "from": {
                        "name": "Cow",
                        "wallet": "0xCD2a3d9F938E13CD947Ec05AbC7FE734Df8DD826",
                    },
                    "to": {
                        "name": "Bob",
                        "wallet": "0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB",
                    },
                    "cc": [
                        {
                            "name": "Alice",
                            "wallet": "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                        },
                        {
                            "name": "Dot",
                            "wallet": "0xdddddddddddddddddddddddddddddddddddddddd",
                        },
                    ],
                    "contents": "Hello, Bob!",
                },
            },
        ),
        (
            "Custom type",
            "2f1c830ad734e08c06419c229b6bb26e0fb4134b5c04a4dea2163171b79683eb",
            {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                    ],
                    "Person": [
                        {"name": "name", "type": "string"},
                    ],
                },
                "primaryType": "Person",
                "domain": {
                    "name": "Name",
                },
                "message": {
                    "name": "Bob",
                },
            },
        ),
        (
            "Recursive custom type",
            "36c7cd01046282632deb49c4095ec5c504502369acfed60c1120b7d7f32740a9",
            {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                    ],
                    "Person": [
                        {"name": "name", "type": "string"},
                        {"name": "friends", "type": "Person[]"},
                    ],
                },
                "primaryType": "Person",
                "domain": {
                    "name": "Name",
                },
                "message": {
                    "name": "Bob",
                    "friends": [
                        {
                            "name": "Charlie",
                            "friends": [],
                        }
                    ],
                },
            },
        ),
        (
            "Unused custom type",
            "2f1c830ad734e08c06419c229b6bb26e0fb4134b5c04a4dea2163171b79683eb",
            {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                    ],
                    "Person": [
                        {"name": "name", "type": "string"},
                    ],
                    "Pet": [
                        {"name": "animal", "type": "string"},
                        {"name": "age", "type": "uint256"},
                    ],
                },
                "primaryType": "Person",
                "domain": {
                    "name": "Name",
                },
                "message": {
                    "name": "Bob",
                },
            },
        ),
        (
            "Custom type with extra properties in message",
            "2f1c830ad734e08c06419c229b6bb26e0fb4134b5c04a4dea2163171b79683eb",
            {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                    ],
                    "Person": [
                        {"name": "name", "type": "string"},
                    ],
                },
                "primaryType": "Person",
                "domain": {
                    "name": "Name",
                },
                "message": {
                    "name": "Bob",
                    "age": 33,
                },
            },
        ),
    ),
)
def test_encode_structured_data_pass(_input_type, expected_esd_hash, message_to_encode):
    assert (
        _hash_eip191_message(encode_structured_data(message_to_encode)).hex()
        == expected_esd_hash
    )


@pytest.mark.parametrize(
    "_input_type, expected_esd_err, message_to_encode",
    (
        (
            "Custom type with extra properties in types",
            {
                "expected_exception": KeyError,
                "match": "age",
            },
            {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                    ],
                    "Person": [
                        {"name": "name", "type": "string"},
                        {"name": "age", "type": "uint256"},
                    ],
                },
                "primaryType": "Person",
                "domain": {
                    "name": "Name",
                },
                "message": {
                    "name": "Bob",
                },
            },
        ),
        (
            "Atomic type with `None` input",
            {
                "expected_exception": ValueError,
                "match": "Missing value for field address of type address",
            },
            {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                    ],
                    "Person": [
                        {"name": "name", "type": "string"},
                        {"name": "address", "type": "address"},
                    ],
                },
                "primaryType": "Person",
                "domain": {
                    "name": "Name",
                },
                "message": {
                    "name": "Bob",
                    "address": None,
                },
            },
        ),
        (
            "Atomic type missing",
            {
                "expected_exception": KeyError,
                "match": "address",
            },
            {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                    ],
                    "Person": [
                        {"name": "name", "type": "string"},
                        {"name": "address", "type": "address"},
                    ],
                },
                "primaryType": "Person",
                "domain": {
                    "name": "Name",
                },
                "message": {
                    "name": "Bob",
                },
            },
        ),
        (
            "Dynamic type with `None` input",
            {
                "expected_exception": ValueError,
                "match": "Missing value for field motto of type string",
            },
            {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                    ],
                    "Person": [
                        {"name": "name", "type": "string"},
                        {"name": "motto", "type": "string"},
                    ],
                },
                "primaryType": "Person",
                "domain": {
                    "name": "Name",
                },
                "message": {
                    "name": "Bob",
                    "motto": None,
                },
            },
        ),
        (
            "Dynamic type missing",
            {
                "expected_exception": KeyError,
                "match": "motto",
            },
            {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                    ],
                    "Person": [
                        {"name": "name", "type": "string"},
                        {"name": "motto", "type": "string"},
                    ],
                },
                "primaryType": "Person",
                "domain": {
                    "name": "Name",
                },
                "message": {
                    "name": "Bob",
                },
            },
        ),
        (
            "Custom type with `None` input",
            {
                "expected_exception": ValueError,
                "match": "Missing value for field friend of type Person",
            },
            {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                    ],
                    "Person": [
                        {"name": "name", "type": "string"},
                        {"name": "friend", "type": "Person"},
                    ],
                },
                "primaryType": "Person",
                "domain": {
                    "name": "Name",
                },
                "message": {
                    "name": "Bob",
                    "friend": None,
                },
            },
        ),
        (
            "Custom type missing",
            {
                "expected_exception": KeyError,
                "match": "friend",
            },
            {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                    ],
                    "Person": [
                        {"name": "name", "type": "string"},
                        {"name": "friend", "type": "Person"},
                    ],
                },
                "primaryType": "Person",
                "domain": {
                    "name": "Name",
                },
                "message": {
                    "name": "Bob",
                },
            },
        ),
        (
            "Unrecognized primary type",
            {
                "expected_exception": ValidationError,
                "match": "The Primary Type `Person` is not present in the `types` attribute",  # noqa: E501
            },
            {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                    ],
                    "Human": [
                        {"name": "name", "type": "string"},
                    ],
                },
                "primaryType": "Person",
                "domain": {
                    "name": "Name",
                },
                "message": {
                    "name": "Bob",
                },
            },
        ),
    ),
)
def test_encode_structured_data_fail(_input_type, expected_esd_err, message_to_encode):
    with pytest.raises(**expected_esd_err):
        encode_structured_data(message_to_encode)
