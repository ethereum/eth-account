from typing import (
    List,
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

PrivateKeyType = Union[bytes, int, HexStr, PrivateKey]
Blobs = List[Union[bytes, HexBytes]]
