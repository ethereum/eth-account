from typing import (
    Any,
    Dict,
    List,
    Tuple,
)

from eth_abi import (
    encode,
)
from eth_utils import (
    is_hexstr,
    keccak,
    to_bytes,
)


def _get_EIP712_solidity_types():
    types = ["bool", "address", "string", "bytes"]
    ints = [f"int{(x + 1) * 8}" for x in range(32)]
    uints = [f"uint{(x + 1) * 8}" for x in range(32)]
    bytes_ = [f"bytes{x + 1}" for x in range(32)]
    return types + ints + uints + bytes_


EIP712_SOLIDITY_TYPES = _get_EIP712_solidity_types()


def _is_array_type(type_: str) -> bool:
    return type_.endswith("]")


# strip all brackets: Person[][] -> Person
def _parse_core_array_type(type_: str) -> str:
    if _is_array_type(type_):
        type_ = type_[: type_.index("[")]
    return type_


# strip outermost brackets: Person[][] -> Person[]
def _parse_inner_array_type(type_: str) -> str:
    if _is_array_type(type_):
        type_ = type_[: type_.rindex("[")]
    return type_


def _get_primary_type(types: Dict[str, List[Dict[str, str]]]) -> str:
    custom_types = set(types.keys())
    custom_types_that_are_deps = set()

    for type in custom_types:
        type_fields = types[type]
        for field in type_fields:
            parsed_type = _parse_core_array_type(field["type"])
            if parsed_type in custom_types and parsed_type != type:
                custom_types_that_are_deps.add(parsed_type)

    primary_type = list(custom_types.difference(custom_types_that_are_deps))
    if len(primary_type) == 1:
        return primary_type[0]
    else:
        raise ValueError("Unable to determine primary type")


def encode_field(
    types: Dict[str, List[Dict[str, str]]],
    name: str,
    type_: str,
    value: Any,
) -> Tuple[str, bytes]:
    if type_ in types.keys():
        # type is a custom type
        if value is None:
            return (
                "bytes32",
                b"\x00" * 32,
            )
        else:
            return (
                "bytes32",
                keccak(encode_data(type_, types, value)),
            )

    if type_ in ["string", "bytes"] and value is None:
        return (
            "bytes32",
            b"",
        )

    # None is allowed only for custom and dynamic types
    if value is None:
        raise ValueError(f"missing value for field {name} of type {type_}")

    if type_ == "bytes":
        if is_hexstr(value):
            value = to_bytes(hexstr=value)
        else:
            value = to_bytes(value)
        return ("bytes32", keccak(value))

    if type_ == "string":
        if isinstance(value, int):
            value = to_bytes(value)
        else:
            value = to_bytes(text=value)
        return ("bytes32", keccak(value))

    if _is_array_type(type_):
        type_ = _parse_inner_array_type(type_)
        type_value_pairs = [encode_field(types, name, type_, item) for item in value]
        data_types, data_hashes = zip(*type_value_pairs)
        return ("bytes32", keccak(encode(data_types, data_hashes)))

    return (type_, value)


def find_type_dependencies(type_, types, results=None):
    if results is None:
        results = set()

    # a type must be a string
    if not isinstance(type_, str):
        raise ValueError(
            "Invalid find_type_dependencies input: expected string, got "
            f"{type_} of type {type(type_)}"
        )
    # get core type if it's an array type
    type_ = _parse_core_array_type(type_)

    # don't look for dependencies of solidity types
    if type_ in EIP712_SOLIDITY_TYPES:
        return results

    # found a type that isn't defined
    if type_ not in types:
        raise ValueError(f"No definition of type {type_}")

    # found a type that's already been added
    if type_ in results:
        return results

    results.add(type_)

    for field in types[type_]:
        find_type_dependencies(field["type"], types, results)
    return results


def encode_type(type_: str, types: Dict[str, List[Dict[str, str]]]) -> str:
    result = ""
    unsorted_deps = find_type_dependencies(type_, types)
    if type_ in unsorted_deps:
        unsorted_deps.remove(type_)

    deps = [type_] + sorted(list(unsorted_deps))
    for type_ in deps:
        children_list = []
        for child in types[type_]:
            child_type = child["type"]
            child_name = child["name"]
            children_list.append(f"{child_type} {child_name}")

        result += f"{type_}({','.join(children_list)})"

    return result


def hash_type(type_: str, types: Dict[str, List[Dict[str, str]]]) -> bytes:
    return keccak(text=encode_type(type_, types))


def encode_data(
    type_: str,
    types: Dict[str, List[Dict[str, str]]],
    data: Dict[str, Any],
) -> bytes:
    encoded_types = ["bytes32"]
    encoded_values = [hash_type(type_, types)]

    for field in types[type_]:
        type, value = encode_field(
            types,
            field["name"],
            field["type"],
            data.get(field["name"]),
        )
        encoded_types.append(type)
        encoded_values.append(value)

    return encode(encoded_types, encoded_values)


def hash_struct(
    type_: str,
    types: Dict[str, List[Dict[str, str]]],
    data: Dict[str, Any],
) -> bytes:
    encoded = encode_data(type_, types, data)
    hashed = keccak(encoded)
    return hashed


def hash_domain(domain_data: Dict[str, Any]) -> bytes:
    EIP712_domain_map = {
        "name": {"name": "name", "type": "string"},
        "version": {"name": "version", "type": "string"},
        "chainId": {"name": "chainId", "type": "uint256"},
        "verifyingContract": {"name": "verifyingContract", "type": "address"},
        "salt": {"name": "salt", "type": "bytes32"},
    }

    for k in domain_data.keys():
        if k not in EIP712_domain_map.keys():
            raise ValueError(f"Invalid domain key: {k}")

    domain_types = {
        "EIP712Domain": [
            EIP712_domain_map[k] for k in domain_data.keys() if k in domain_data
        ]
    }

    return hash_struct("EIP712Domain", domain_types, domain_data)


def hash_EIP712_message(
    message_types: Dict[str, List[Dict[str, str]]],
    message_data: Dict[str, Any],
) -> bytes:
    primary_type = _get_primary_type(message_types)
    return keccak(encode_data(primary_type, message_types, message_data))


"""

def _fixInt(v):
    if type(v) == str:
        base = 16 if "0x" in v else 10
        return int(v, base)
    elif type(v) == int:
        return v
    return None


def _fixByte(v):
    if type(v) == str and len(v) % 2 == 0:
        newValue = v
        if "0x" in v:
            newValue = newValue.replace("0x", "")
        return bytes.fromhex(newValue)
    elif type(v) == list:
        testList = [0 <= _v <= 255 for _v in v]
        if all(testList):
            return bytes(v)
    return None


def _fix(v, tp, types):
    isArray = "[" in tp and "]" in tp
    if isArray:
        tp = tp[: tp.index("[")]
    if tp in [
        "uint8",
        "uint16",
        "uint32",
        "uint64",
        "uint128",
        "uint256",
        "uint512",
        "int8",
        "int16",
        "int32",
        "int64",
        "int128",
        "int256",
        "int512",
    ]:
        if isArray:
            r = []
            for i, _ in enumerate(v):
                newV = _fixInt(v[i])
                if newV is not None:
                    r.append(newV)
                else:
                    return None
            return r
        else:
            return _fixInt(v)

    elif tp in ["bytes1", "bytes32", "bytes"]:
        if isArray:
            r = []
            for i, _ in enumerate(v):
                newV = _fixByte(v[i])
                if newV is not None:
                    r.append(newV)
                else:
                    return None
            return r
        else:
            return _fixByte(v)
    elif tp == "address":
        return v
    elif tp == "string":
        return v
    else:  # custom type
        if not (tp in types):
            return None
        newTypes = types[tp]
        if isArray:
            r = []
            for i, _ in enumerate(v):
                newV = {}
                for tInfo in newTypes:
                    key = tInfo["name"]
                    tp = tInfo["type"]
                    newV[key] = _fix(v[i][key], tp, types)
                r.append(newV)
            return r
        else:
            newV = {}
            for tInfo in newTypes:
                key = tInfo["name"]
                tp = tInfo["type"]
                newV[key] = _fix(v[key], tp, types)
            return newV
"""
