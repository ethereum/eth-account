from typing import (
    Dict,
    NewType,
    Sequence,
    TypedDict,
    Union,
)

from eth_keys.datatypes import (
    PrivateKey,
)
from eth_typing import (
    Address,
    ChecksumAddress,
    HexStr,
)
from hexbytes import (
    HexBytes,
)

Blobs = Sequence[Union[bytes, HexBytes]]
Bytes32 = bytes
PrivateKeyType = Union[Bytes32, int, HexStr, PrivateKey]

AccessList = Sequence[Dict[str, Union[HexStr, Sequence[HexStr]]]]
RLPStructuredAccessList = Sequence[Sequence[Union[HexStr, Sequence[HexStr]]]]

# TxParams = Dict[str, Union[AccessList, bytes, HexStr, int]]


class AccessListEntry(TypedDict):
    address: HexStr
    storageKeys: Sequence[HexStr]


AccessList = NewType("AccessList", Sequence[AccessListEntry])

Nonce = NewType("Nonce", int)
Wei = NewType("Wei", int)

TxParams = TypedDict(
    "TxParams",
    {
        "accessList": AccessList,
        "blobVersionedHashes": Sequence[Union[str, HexStr, bytes, HexBytes]],
        "chainId": int,
        "data": Union[bytes, HexStr],
        # addr or ens
        "from": Union[Address, ChecksumAddress, str],
        "gas": int,
        # legacy pricing
        "gasPrice": Wei,
        "maxFeePerBlobGas": Union[str, Wei],
        # dynamic fee pricing
        "maxFeePerGas": Union[str, Wei],
        "maxPriorityFeePerGas": Union[str, Wei],
        "nonce": Nonce,
        # addr or ens
        "to": Union[Address, ChecksumAddress, str],
        "type": Union[int, HexStr],
        "value": Wei,
    },
    total=False,
)
