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
    HexStr,
)
from hexbytes import (
    HexBytes,
)

Blobs = Sequence[Union[bytes, HexBytes]]
PrivateKeyType = Union[bytes, int, HexStr, PrivateKey]


# Same as in web3.types
class AccessListEntry(TypedDict):
    address: HexStr
    storageKeys: Sequence[HexStr]


# Same as in web3.types
AccessList = NewType("AccessList", Sequence[AccessListEntry])

TransactionDictType = Dict[str, Union[AccessList, bytes, HexStr, int]]
