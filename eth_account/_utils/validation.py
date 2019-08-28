from typing import (
    Union,
)

from eth_utils import (
    is_binary_address,
    is_checksum_address,
)


def is_valid_address(value: Union[bytes, str]) -> bool:
    if is_binary_address(value):
        return True
    elif is_checksum_address(value):
        return True
    else:
        return False
