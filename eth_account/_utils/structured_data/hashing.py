from collections import (
    Iterable,
)
import json

from eth_abi import (
    encode_abi,
    is_encodable,
)
from eth_abi.grammar import (
    parse,
)
from eth_utils import (
    keccak,
    to_tuple,
)

from .validation import (
    validate_structured_data,
)


def get_dependencies(primary_type, types):
    """
    Perform DFS to get all the dependencies of the primary_type
    """
    deps = set()
    struct_names_yet_to_be_expanded = [primary_type]

    while len(struct_names_yet_to_be_expanded) > 0:
        struct_name = struct_names_yet_to_be_expanded.pop()

        deps.add(struct_name)
        fields = types[struct_name]
        for field in fields:
            if field["type"] not in types:
                # We don't need to expand types that are not user defined (customized)
                continue
            elif field["type"] in deps:
                # skip types that we have already encountered
                continue
            else:
                # Custom Struct Type
                struct_names_yet_to_be_expanded.append(field["type"])

    # Don't need to make a struct as dependency of itself
    deps.remove(primary_type)

    return tuple(deps)


def field_identifier(field):
    """
    Given a ``field`` of the format {'name': NAME, 'type': TYPE},
    this function converts it to ``TYPE NAME``
    """
    return "{0} {1}".format(field["type"], field["name"])


def encode_struct(struct_name, struct_field_types):
    return "{0}({1})".format(
        struct_name,
        ','.join(map(field_identifier, struct_field_types)),
    )


def encode_type(primary_type, types):
    """
    The type of a struct is encoded as name ‖ "(" ‖ member₁ ‖ "," ‖ member₂ ‖ "," ‖ … ‖ memberₙ ")"
    where each member is written as type ‖ " " ‖ name.
    """
    # Getting the dependencies and sorting them alphabetically as per EIP712
    deps = get_dependencies(primary_type, types)
    sorted_deps = (primary_type,) + tuple(sorted(deps))

    result = ''.join(
        [
            encode_struct(struct_name, types[struct_name])
            for struct_name in sorted_deps
        ]
    )
    return result


def hash_struct_type(primary_type, types):
    return keccak(text=encode_type(primary_type, types))


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


def is_array_type(type):
    # Identify if type such as "person[]" or "person[2]" is an array
    abi_type = parse(type)
    return abi_type.is_array


def get_array_dimensions(data):
    """
    Given an array type data item, check that it is an array and
    return the dimensions as a tuple.
    Ex: get_array_dimensions([[1, 2, 3], [4, 5, 6]]) returns (2, 3)
    """
    if not isinstance(data, list) and not isinstance(data, tuple):
        # Not checking for Iterable instance, because even Dictionaries and strings
        # are considered as iterables, but that's not what we want the condition to be.
        return ()

    expected_dimensions = get_array_dimensions(data[0])
    for index in range(1, len(data)):
        # 1 dimension less sub-arrays should all have the same dimensions to be a valid array
        if get_array_dimensions(data[index]) != expected_dimensions:
            raise TypeError("Not a valid array or incomplete array")

    return (len(data),) + expected_dimensions


@to_tuple
def flatten_multidimensional_array(array):
    for item in array:
        if isinstance(item, Iterable) and not isinstance(item, str):
            for x in flatten_multidimensional_array(item):
                yield x
        else:
            yield item


@to_tuple
def _encode_data(primary_type, types, data):
    # Add typehash
    yield "bytes32", hash_struct_type(primary_type, types)

    # Add field contents
    for field in types[primary_type]:
        value = data[field["name"]]
        if field["type"] == "string":
            if not isinstance(value, str):
                raise TypeError(
                    "Value of `{0}` ({2}) in the struct `{1}` is of the type `{3}`, but expected "
                    "string value".format(
                        field["name"],
                        primary_type,
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
                        primary_type,
                        value,
                        type(value),
                    )
                )
            # Special case where the values need to be keccak hashed before they are encoded
            hashed_value = keccak(primitive=value)
            yield "bytes32", hashed_value
        elif field["type"] in types:
            # This means that this type is a user defined type
            hashed_value = keccak(primitive=encode_data(field["type"], types, value))
            yield "bytes32", hashed_value
        elif is_array_type(field["type"]):
            # Get the dimensions from the value
            array_dimensions = get_array_dimensions(value)
            # Get the dimensions from what was declared in the schema
            parsed_type = parse(field["type"])
            for i in range(len(array_dimensions)):
                if len(parsed_type.arrlist[i]) == 0:
                    # Skip empty or dynamically declared dimensions
                    continue
                if array_dimensions[i] != parsed_type.arrlist[i][0]:
                    # Dimensions should match with declared schema
                    raise TypeError(
                        "Array data `{0}` has dimensions `{1}` whereas the "
                        "schema has dimensions `{2}`".format(
                            value,
                            array_dimensions,
                            tuple(map(lambda x: x[0], parsed_type.arrlist)),
                        )
                    )

            array_items = flatten_multidimensional_array(value)
            array_items_encoding = [
                encode_data(parsed_type.base, types, array_item)
                for array_item in array_items
            ]
            concatenated_array_encodings = ''.join(array_items_encoding)
            hashed_value = keccak(concatenated_array_encodings)
            yield "bytes32", hashed_value
        else:
            # First checking to see if type is valid as per abi
            if not is_valid_abi_type(field["type"]):
                raise TypeError(
                    "Received Invalid type `{0}` in the struct `{1}`".format(
                        field["type"],
                        primary_type,
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
                        primary_type,
                        value,
                        type(value),
                        field["type"],
                    )
                )


def encode_data(primaryType, types, data):
    data_types_and_hashes = _encode_data(primaryType, types, data)
    data_types, data_hashes = zip(*data_types_and_hashes)
    return encode_abi(data_types, data_hashes)


def hash_struct(structured_json_string_data, is_domain_separator=False):
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
    return keccak(encode_data(primaryType, types, data))
