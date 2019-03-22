import json

from eth_abi import (
    encode_abi,
    is_encodable,
)
from eth_utils import (
    keccak,
    to_tuple,
)

from .validation import (
    validate_structured_data,
)


def dependencies(primaryType, types):
    """
    Perform DFS to get all the dependencies of the primaryType
    """
    deps = set()
    struct_names_yet_to_be_expanded = [primaryType]

    while len(struct_names_yet_to_be_expanded) > 0:
        struct_name = struct_names_yet_to_be_expanded.pop()

        deps.add(struct_name)
        fields = types[struct_name]
        for field in fields:
            # If this struct type has already been seen, then don't expand on it'
            if field["type"] in deps:
                continue
            # If this struct type is not a customized type, then no need to expand
            elif field["type"] not in types:
                continue
            # Custom Struct Type
            else:
                struct_names_yet_to_be_expanded.append(field["type"])

    # Don't need to make a struct as dependency of itself
    deps.remove(primaryType)

    return tuple(deps)


def dict_to_type_name_converter(field):
    """
    Given a dictionary ``field`` of type {'name': NAME, 'type': TYPE},
    this function converts it to ``TYPE NAME``
    """
    return "{0} {1}".format(field["type"], field["name"])


def encode_struct(struct_name, struct_types):
    return "{0}({1})".format(
        struct_name,
        ','.join(map(dict_to_type_name_converter, struct_types)),
    )


def encodeType(primaryType, types):
    """
    The type of a struct is encoded as name ‖ "(" ‖ member₁ ‖ "," ‖ member₂ ‖ "," ‖ … ‖ memberₙ ")"
    where each member is written as type ‖ " " ‖ name.
    """
    # Getting the dependencies and sorting them alphabetically as per EIP712
    deps = dependencies(primaryType, types)
    sorted_deps = (primaryType,) + tuple(sorted(deps))

    result = ''.join(
        [
            encode_struct(struct_name, types[struct_name])
            for struct_name in sorted_deps
        ]
    )
    return result


def typeHash(primaryType, types):
    return keccak(text=encodeType(primaryType, types))


def is_valid_abi_type(type_name):
    """
    This function is used to make sure that the ``type_name`` is a valid ABI Type.

    Please note that this is a temporary function and should be replaced by the corresponding
    ABI function, once the following issue has been resolved.
    https://github.com/ethereum/eth-abi/issues/125
    """
    valid_abi_types = {"address", "bool", "bytes", "int", "string", "uint"}
    is_bytesN = type_name.startswith("bytes") and 1 <= int(type_name[5:]) <= 32
    is_intN = (
        type_name.startswith("int") and
        8 <= int(type_name[3:]) <= 256 and
        int(type_name[3:]) % 8 == 0
    )
    is_uintN = (
        type_name.startswith("uint") and
        8 <= int(type_name[4:]) <= 256 and
        int(type_name[4:]) % 8 == 0
    )

    if type_name in valid_abi_types:
        return True
    elif is_bytesN:
        # bytes1 to bytes32
        return True
    elif is_intN:
        # int8 to int256
        return True
    elif is_uintN:
        # uint8 to uint256
        return True

    return False


@to_tuple
def _encodeData(primaryType, types, data):
    # Add typehash
    yield "bytes32", typeHash(primaryType, types)

    # Add field contents
    for field in types[primaryType]:
        value = data[field["name"]]
        if field["type"] == "string":
            if not isinstance(value, str):
                raise TypeError(
                    "Value of `{0}` ({2}) in the struct `{1}` is of the type `{3}`, but expected "
                    "string value".format(
                        field["name"],
                        primaryType,
                        value,
                        type(value),
                    )
                )
            # Special case where the values need to be keccak hashed before they are encoded
            hashed_value = keccak(text=value)
            yield "bytes32", hashed_value
        elif field["type"] == "bytes":
            if not isinstance(value, bytes):
                raise TypeError(
                    "Value of `{0}` ({2}) in the struct `{1}` is of the type `{3}`, but expected "
                    "bytes value".format(
                        field["name"],
                        primaryType,
                        value,
                        type(value),
                    )
                )
            # Special case where the values need to be keccak hashed before they are encoded
            hashed_value = keccak(primitive=value)
            yield "bytes32", hashed_value
        elif field["type"] in types:
            # This means that this type is a user defined type
            hashed_value = keccak(primitive=encodeData(field["type"], types, value))
            yield "bytes32", hashed_value
        elif field["type"][-1] == "]":
            # TODO: Replace the above conditionality with Regex for identifying arrays declaration
            raise NotImplementedError("TODO: Arrays currently unimplemented in encodeData")
        else:
            # First checking to see if type is valid as per abi
            if not is_valid_abi_type(field["type"]):
                raise TypeError(
                    "Received Invalid type `{0}` in the struct `{1}`".format(
                        field["type"],
                        primaryType,
                    )
                )

            # Next see if the data fits the specified encoding type
            if is_encodable(field["type"], value):
                # field["type"] is a valid type and this value corresponds to that type.
                yield field["type"], value
            else:
                raise TypeError(
                    "Value of `{0}` ({2}) in the struct `{1}` is of the type `{3}`, but expected "
                    "{4} value".format(
                        field["name"],
                        primaryType,
                        value,
                        type(value),
                        field["type"],
                    )
                )


def encodeData(primaryType, types, data):
    data_types_and_hashes = _encodeData(primaryType, types, data)
    data_types, data_hashes = zip(*data_types_and_hashes)
    return encode_abi(data_types, data_hashes)


def hashStruct(structured_json_string_data, is_domain_separator=False):
    """
    The structured_json_string_data is expected to have the ``types`` attribute and
    the ``primaryType``, ``message``, ``domain`` attribute.
    The ``is_domain_separator`` variable is used to calculate the ``hashStruct`` as
    part of the ``domainSeparator`` calculation.
    """
    structured_data = json.loads(structured_json_string_data)
    validate_structured_data(structured_data)

    types = structured_data["types"]
    if is_domain_separator:
        primaryType = "EIP712Domain"
        data = structured_data["domain"]
    else:
        primaryType = structured_data["primaryType"]
        data = structured_data["message"]
    return keccak(encodeData(primaryType, types, data))
