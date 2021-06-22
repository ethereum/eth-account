from eth_utils import (
    is_binary_address,
    is_checksum_address,
)

from eth_utils.curried import (
    hexstr_if_str,
    to_int,
    apply_one_of_formatters,
    is_string,
    to_bytes,
    is_bytes,
    is_integer,
    is_0x_prefixed,
)

from cytoolz import (
    identity,
)

VALID_EMPTY_ADDRESSES = {None, b'', ''}


def is_none(val):
    return val is None


def is_valid_address(value):
    if is_binary_address(value):
        return True
    elif is_checksum_address(value):
        return True
    else:
        return False


def is_int_or_prefixed_hexstr(val):
    if is_integer(val):
        return True
    elif isinstance(val, str) and is_0x_prefixed(val):
        return True
    else:
        return False


def is_empty_or_checksum_address(val):
    if val in VALID_EMPTY_ADDRESSES:
        return True
    else:
        return is_valid_address(val)


TRANSACTION_FORMATTERS = {
    'nonce': hexstr_if_str(to_int),
    'gasPrice': hexstr_if_str(to_int),
    'gas': hexstr_if_str(to_int),
    'to': apply_one_of_formatters((
        (is_string, hexstr_if_str(to_bytes)),
        (is_bytes, identity),
        (is_none, lambda val: b''),
    )),
    'value': hexstr_if_str(to_int),
    'data': hexstr_if_str(to_bytes),
    'v': hexstr_if_str(to_int),
    'r': hexstr_if_str(to_int),
    's': hexstr_if_str(to_int),
}

TRANSACTION_VALID_VALUES = {
    'nonce': is_int_or_prefixed_hexstr,
    'gasPrice': is_int_or_prefixed_hexstr,
    'gas': is_int_or_prefixed_hexstr,
    'to': is_empty_or_checksum_address,
    'value': is_int_or_prefixed_hexstr,
    'data': lambda val: isinstance(val, (int, str, bytes, bytearray)),
    'chainId': lambda val: val is None or is_int_or_prefixed_hexstr(val),
}
