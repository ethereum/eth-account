from collections.abc import (
    Sequence,
)
import enum
from typing import (
    Any,
    TypedDict,
    Union,
)

from eth_keys.datatypes import (
    PrivateKey,
)
from eth_typing import (
    HexAddress,
    HexStr,
)
from hexbytes import (
    HexBytes,
)

Blobs = Sequence[Union[bytes, HexBytes]]
Bytes32 = bytes
PrivateKeyType = Union[Bytes32, int, HexStr, PrivateKey]


class AccessListEntry(TypedDict):
    address: HexStr
    storageKeys: Sequence[HexStr]


AccessList = Sequence[AccessListEntry]
RLPStructuredAccessList = Sequence[tuple[HexStr, Sequence[HexStr]]]


class AuthorizationDict(TypedDict):
    chainId: int
    address: HexAddress
    nonce: int


class SignedAuthorizationDict(AuthorizationDict):
    yParity: int
    r: HexStr
    s: HexStr


AuthorizationList = Sequence[SignedAuthorizationDict]
RLPStructuredAuthorizationList = Sequence[
    tuple[int, HexAddress, int, int, HexStr, HexStr]
]

TransactionDictType = dict[str, Union[AccessList, bytes, HexStr, int]]


class Language(enum.Enum):
    CHINESE_SIMPLIFIED = "chinese_simplified"
    CHINESE_TRADITIONAL = "chinese_traditional"
    CZECH = "czech"
    ENGLISH = "english"
    FRENCH = "french"
    ITALIAN = "italian"
    JAPANESE = "japanese"
    KOREAN = "korean"
    SPANISH = "spanish"

    def __lt__(self, other: Any) -> Any:
        if other.__class__ is Language:
            return self.value < other.value
        return NotImplemented
