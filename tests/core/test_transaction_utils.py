import pytest

from eth_account._utils.transaction_utils import (
    _access_list_rlp_to_rpc_structure,
    _access_list_rpc_to_rlp_structure,
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
