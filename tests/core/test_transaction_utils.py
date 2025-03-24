import pytest
from typing import (
    List,
)

from eth_keys.datatypes import (
    Signature,
)
from hexbytes import (
    HexBytes,
)

from eth_account._utils.transaction_utils import (
    _access_list_rlp_to_rpc_structure,
    _access_list_rpc_to_rlp_structure,
    json_serialize_classes_in_transaction,
)
from eth_account.datastructures import (
    CustomPydanticModel,
    SignedSetCodeAuthorization,
)

# access list example from EIP-2930
RLP_STRUCTURED_ACCESS_LIST = [
    (
        "0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae",
        (
            "0x0000000000000000000000000000000000000000000000000000000000000003",
            "0x0000000000000000000000000000000000000000000000000000000000000007",
        ),
    ),
    ("0xbb9bc244d798123fde783fcc1c72d3bb8c189413", ()),
]

RPC_STRUCTURED_ACCESS_LIST = [
    {
        "address": "0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae",
        "storageKeys": (
            "0x0000000000000000000000000000000000000000000000000000000000000003",
            "0x0000000000000000000000000000000000000000000000000000000000000007",
        ),
    },
    {"address": "0xbb9bc244d798123fde783fcc1c72d3bb8c189413", "storageKeys": ()},
]


TEST_SIGNED_AUTHORIZATION = SignedSetCodeAuthorization(
    chain_id=22,
    address=b"\x00" * 19 + b"\x01",
    nonce=1999,
    y_parity=1,
    r=123456789,
    s=987654321,
    signature=Signature(b"\x00" * 65),
    authorization_hash=HexBytes("0x"),
)


class PydanticTestClassInner(CustomPydanticModel):
    int_value: int
    str_value: str
    authorization_list: List[SignedSetCodeAuthorization]
    excluded_field1: str
    excluded_field2: int

    _exclude = {"excluded_field1", "excluded_field2"}


class PydanticTestClass(CustomPydanticModel):
    int_value: int
    nested_model: PydanticTestClassInner
    excluded_field1: str
    excluded_field2: int
    excluded_field3: HexBytes

    _exclude = {"excluded_field1", "excluded_field2", "excluded_field3"}


@pytest.mark.parametrize(
    "access_list",
    (
        RPC_STRUCTURED_ACCESS_LIST,
        tuple(RPC_STRUCTURED_ACCESS_LIST),
    ),
)
def test_access_list_rpc_to_rlp_structure(access_list):
    rlp_structured_access_list = _access_list_rpc_to_rlp_structure(access_list)
    assert rlp_structured_access_list == tuple(RLP_STRUCTURED_ACCESS_LIST)


@pytest.mark.parametrize(
    "access_list",
    (
        RLP_STRUCTURED_ACCESS_LIST,
        tuple(RLP_STRUCTURED_ACCESS_LIST),
    ),
)
def test_access_list_rpc_to_rlp_structure_raises_when_not_rpc_access_list(access_list):
    with pytest.raises(
        ValueError,
        match="provided object not formatted as JSON-RPC-structured access list",
    ):
        _access_list_rpc_to_rlp_structure(access_list)


@pytest.mark.parametrize(
    "access_list",
    (
        RLP_STRUCTURED_ACCESS_LIST,
        tuple(RLP_STRUCTURED_ACCESS_LIST),
    ),
)
def test_access_list_rlp_to_rpc_structure(access_list):
    rpc_structured_access_list = _access_list_rlp_to_rpc_structure(access_list)
    assert rpc_structured_access_list == tuple(RPC_STRUCTURED_ACCESS_LIST)


@pytest.mark.parametrize(
    "access_list",
    (
        RPC_STRUCTURED_ACCESS_LIST,
        tuple(RPC_STRUCTURED_ACCESS_LIST),
    ),
)
def test_access_list_rlp_to_rpc_structure_raises_when_not_rlp_access_list(access_list):
    with pytest.raises(
        ValueError, match="provided object not formatted as rlp-structured access list"
    ):
        _access_list_rlp_to_rpc_structure(access_list)


def test_class_serializer():
    serialized = json_serialize_classes_in_transaction(
        {
            "testPydanticModel": PydanticTestClass(
                int_value=1,
                nested_model=PydanticTestClassInner(
                    int_value=2,
                    str_value="3",
                    authorization_list=[TEST_SIGNED_AUTHORIZATION],
                    excluded_field1="4",
                    excluded_field2=5,
                ),
                excluded_field1="6",
                excluded_field2=7,
                excluded_field3=HexBytes("0x08"),
            ),
        }
    )

    assert serialized == {
        "testPydanticModel": {
            "intValue": 1,
            "nestedModel": {
                "intValue": 2,
                "strValue": "3",
                "authorizationList": [
                    {
                        "chainId": 22,
                        "address": "0x" + "00" * 19 + "01",
                        "nonce": 1999,
                        "yParity": 1,
                        "r": 123456789,
                        "s": 987654321,
                    }
                ],
            },
        },
    }
