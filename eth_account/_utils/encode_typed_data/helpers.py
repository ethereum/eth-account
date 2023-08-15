from typing import (
    Any,
)


def _get_EIP712_solidity_types():
    types = ["bool", "address", "string", "bytes"]
    ints = [f"int{(x + 1) * 8}" for x in range(32)]
    uints = [f"uint{(x + 1) * 8}" for x in range(32)]
    bytes_ = [f"bytes{x + 1}" for x in range(32)]
    return types + ints + uints + bytes_


EIP712_SOLIDITY_TYPES = _get_EIP712_solidity_types()


def is_array_type(type_: str) -> bool:
    return type_.endswith("]")


# strip all brackets: Person[][] -> Person
def parse_core_array_type(type_: str) -> str:
    if is_array_type(type_):
        type_ = type_[: type_.index("[")]
    return type_


# strip only last set of brackets: Person[3][1] -> Person[3]
def parse_parent_array_type(type_: str) -> str:
    if is_array_type(type_):
        type_ = type_[: type_.rindex("[")]
    return type_


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    elif isinstance(value, int):
        if value == 0:
            return False
        elif value == 1:
            return True
        else:
            raise TypeError(f"Cannot coerce int '{value}' to bool")
    elif isinstance(value, bytes):
        if value == b"\x00":
            return False
        elif value == b"\x01":
            return True
        else:
            raise TypeError(f"Cannot coerce bytes '{value!r}' to bool")
    elif isinstance(value, str):
        if value.lower() in ["false", "0", "0x0"]:
            return False
        elif value.lower() in ["true", "1", "0x1"]:
            return True
        else:
            raise TypeError(f"Cannot coerce string '{value}' to bool")

    else:
        raise TypeError(f"Cannot coerce '{value}' of type '{type(value)}' to bool")
