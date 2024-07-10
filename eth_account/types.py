from typing import (
    Dict,
    Sequence,
    Union,
)

from eth_keys.datatypes import (
    PrivateKey,
)
from eth_typing import (
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

TransactionDictType = Dict[str, Union[AccessList, bytes, HexStr, int]]
