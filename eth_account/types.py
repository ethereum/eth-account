import enum
from typing import (
    Any,
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
