from eth_utils import (
    is_binary_address,
    is_checksum_address,
)


def is_valid_address(value):
    if is_binary_address(value):
        return True
    elif is_checksum_address(value):
        return True
    else:
        return False
