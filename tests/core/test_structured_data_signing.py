import json
import pytest
import re

from eth_utils import (
    ValidationError,
    keccak,
)
from hexbytes import (
    HexBytes,
)

from eth_account import (
    Account,
)
from eth_account._utils.structured_data.hashing import (
    encode_data,
    encode_struct,
    encode_type,
    get_array_dimensions,
    get_dependencies,
    hash_domain,
    hash_message,
    hash_struct_type,
    load_and_validate_structured_message,
)
from eth_account._utils.structured_data.validation import (
    TYPE_REGEX,
)
from eth_account.messages import (
    _hash_eip191_message,
    encode_structured_data,
)


@pytest.fixture
def eip712_example_json_string():
    return open("tests/fixtures/valid_eip712_example.json", "r").read()


@pytest.fixture
def eip712_example_types(eip712_example_json_string):
    return json.loads(eip712_example_json_string)["types"]


@pytest.fixture
def eip712_example_domain_type(eip712_example_json_string):
    return json.loads(eip712_example_json_string)["types"]["EIP712Domain"]


@pytest.fixture
def eip712_example_message(eip712_example_json_string):
    return json.loads(eip712_example_json_string)["message"]


@pytest.fixture
def eip712_example_domain(eip712_example_json_string):
    return json.loads(eip712_example_json_string)["domain"]


@pytest.fixture(params=("text", "dict", "primitive", "hexstr"))
def eip712_message_encodings(request, eip712_example_json_string):
    if request.param == "text":
        return {"text": eip712_example_json_string}
    elif request.param == "primitive":
        return {"primitive": eip712_example_json_string.encode()}
    elif request.param == "dict":
        return {"primitive": json.loads(eip712_example_json_string)}
    elif request.param == "hexstr":
        return {"hexstr": eip712_example_json_string.encode().hex()}
    else:
        raise Exception("Unreachable")


# --- EIP 712 example with added "cc" array field to Mail struct --- #

@pytest.fixture
def eip712_example_with_array_json_string():
    return open("tests/fixtures/valid_eip712_example_with_array.json", "r").read()


@pytest.fixture
def eip712_example_with_array_types(eip712_example_with_array_json_string):
    return json.loads(eip712_example_with_array_json_string)["types"]


@pytest.fixture
def eip712_example_with_array_domain_type(eip712_example_with_array_json_string):
    return json.loads(eip712_example_with_array_json_string)["types"]["EIP712Domain"]


@pytest.fixture
def eip712_example_with_array_message(eip712_example_with_array_json_string):
    return json.loads(eip712_example_with_array_json_string)["message"]


@pytest.fixture
def eip712_example_with_array_domain(eip712_example_with_array_json_string):
    return json.loads(eip712_example_with_array_json_string)["domain"]


@pytest.fixture(params=("text", "dict", "primitive", "hexstr"))
def eip712_with_array_message_encodings(request, eip712_example_with_array_json_string):
    if request.param == "text":
        return {"text": eip712_example_with_array_json_string}
    elif request.param == "primitive":
        return {"primitive": eip712_example_with_array_json_string.encode()}
    elif request.param == "dict":
        return {"primitive": json.loads(eip712_example_with_array_json_string)}
    elif request.param == "hexstr":
        return {"hexstr": eip712_example_with_array_json_string.encode().hex()}
    else:
        raise Exception("Unreachable")


@pytest.mark.parametrize(
    'primary_type, expected',
    (
        ('Mail', ('Person',)),
        ('Person', ()),
    )
)
def test_get_dependencies_eip712(primary_type, expected, eip712_example_types):
    assert get_dependencies(primary_type, eip712_example_types) == expected


@pytest.mark.parametrize(
    'primary_type, expected',
    (
        ('Mail', ('Person',)),
        ('Person', ()),
    )
)
def test_get_dependencies_eip712_with_array(
    primary_type, expected, eip712_example_with_array_types
):
    assert get_dependencies(primary_type, eip712_example_with_array_types) == expected


@pytest.mark.parametrize(
    'struct_name, expected',
    (
        ("Mail", "Mail(Person from,Person to,string contents)"),
        ("Person", "Person(string name,address wallet)"),
        ("EIP712Domain", "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),  # noqa: E501
    )
)
def test_encode_struct_eip712(struct_name, expected, eip712_example_types):
    assert encode_struct(struct_name, eip712_example_types[struct_name]) == expected


@pytest.mark.parametrize(
    'struct_name, expected',
    (
        ("Mail", "Mail(Person from,Person to,Person[] cc,string contents)"),
        ("Person", "Person(string name,address wallet)"),
        ("EIP712Domain", "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),  # noqa: E501
    )
)
def test_encode_struct_eip712_with_array(struct_name, expected, eip712_example_with_array_types):
    assert encode_struct(struct_name, eip712_example_with_array_types[struct_name]) == expected


@pytest.mark.parametrize(
    'primary_type, expected',
    (
        ('Mail', 'Mail(Person from,Person to,string contents)Person(string name,address wallet)'),  # noqa: E501
        ('Person', 'Person(string name,address wallet)'),
    )
)
def test_encode_type_eip712(primary_type, expected, eip712_example_types):
    assert encode_type(primary_type, eip712_example_types) == expected


@pytest.mark.parametrize(
    'primary_type, expected',
    (
        ('Mail', 'Mail(Person from,Person to,Person[] cc,string contents)Person(string name,address wallet)'),  # noqa: E501
        ('Person', 'Person(string name,address wallet)'),
    )
)
def test_encode_type_eip712_with_array(primary_type, expected, eip712_example_with_array_types):
    assert encode_type(primary_type, eip712_example_with_array_types) == expected


@pytest.mark.parametrize(
    'primary_type, expected_hex',
    (
        ('Mail', 'a0cedeb2dc280ba39b857546d74f5549c3a1d7bdc2dd96bf881f76108e23dac2'),
        ('Person', 'b9d8c78acf9b987311de6c7b45bb6a9c8e1bf361fa7fd3467a2163f994c79500'),
    )
)
def test_hash_struct_type_eip712(primary_type, expected_hex, eip712_example_types):
    assert hash_struct_type(primary_type, eip712_example_types).hex() == expected_hex


@pytest.mark.parametrize(
    'primary_type, expected_hex',
    (
        ('Person', 'b9d8c78acf9b987311de6c7b45bb6a9c8e1bf361fa7fd3467a2163f994c79500'),
        ('Mail', 'b19c5c7781083ed7325660d847f8c547b744917d67b38858b00bce7e62a4866b'),
    )
)
def test_hash_struct_type_eip712_with_array(
    primary_type, expected_hex, eip712_example_with_array_types
):
    assert hash_struct_type(primary_type, eip712_example_with_array_types).hex() == expected_hex


def test_encode_data_eip712(eip712_example_types, eip712_example_message):
    primary_type = "Mail"
    expected_hex = (
        "a0cedeb2dc280ba39b857546d74f5549c3a1d7bdc2dd96bf881f76108e23dac2fc71e5fa27ff56c350aa"
        "531bc129ebdf613b772b6604664f5d8dbe21b85eb0c8cd54f074a4af31b4411ff6a60c9719dbd559c221"
        "c8ac3492d9d872b041d703d1b5aadf3154a261abdd9086fc627b61efca26ae5702701d05cd2305f7c52a"
        "2fc8"
    )
    assert encode_data(primary_type, eip712_example_types, eip712_example_message).hex() == expected_hex  # noqa: E501


def test_encode_data_eip712_with_array(
    eip712_example_with_array_types, eip712_example_with_array_message
):
    primary_type = "Mail"
    expected_hex = (
        "b19c5c7781083ed7325660d847f8c547b744917d67b38858b00bce7e62a4866bfc71e5fa27ff56c350aa"
        "531bc129ebdf613b772b6604664f5d8dbe21b85eb0c8cd54f074a4af31b4411ff6a60c9719dbd559c221"
        "c8ac3492d9d872b041d703d1a88b5e35e8f6bccc3d72ef467ed581615888f8cf34df19d068d04225439b"
        "e65ab5aadf3154a261abdd9086fc627b61efca26ae5702701d05cd2305f7c52a2fc8"
    )
    assert encode_data(primary_type, eip712_example_with_array_types, eip712_example_with_array_message).hex() == expected_hex  # noqa: E501


def test_hash_struct_main_message_eip712(eip712_example_json_string):
    structured_data = json.loads(eip712_example_json_string)
    expected_hex = "c52c0ee5d84264471806290a3f2c4cecfc5490626bf912d01f240d7a274b371e"
    assert hash_message(structured_data).hex() == expected_hex


def test_hash_struct_main_message_eip712_with_array(eip712_example_with_array_json_string):
    structured_data = json.loads(eip712_example_with_array_json_string)
    expected_hex = "76649452daa3e4101beef5b01669fd0de45ece35188d529703c73526a2454521"
    assert hash_message(structured_data).hex() == expected_hex


def test_hash_struct_domain_eip712(eip712_example_json_string):
    structured_data = json.loads(eip712_example_json_string)
    expected_hex = 'f2cee375fa42b42143804025fc449deafd50cc031ca257e0b194a650a912090f'
    assert hash_domain(structured_data).hex() == expected_hex


def test_hash_struct_domain_eip712_with_array(eip712_example_with_array_json_string):
    structured_data = json.loads(eip712_example_with_array_json_string)
    expected_hex = 'f2cee375fa42b42143804025fc449deafd50cc031ca257e0b194a650a912090f'
    assert hash_domain(structured_data).hex() == expected_hex


def test_hashed_structured_data_eip712(eip712_message_encodings):
    structured_msg = encode_structured_data(**eip712_message_encodings)
    hashed_structured_msg = _hash_eip191_message(structured_msg)
    expected_hex = 'be609aee343fb3c4b28e1df9e632fca64fcfaede20f02e86244efddf30957bd2'
    assert hashed_structured_msg.hex() == expected_hex


def test_hashed_structured_data_eip127_with_array(eip712_with_array_message_encodings):
    structured_msg = encode_structured_data(**eip712_with_array_message_encodings)
    hashed_structured_msg = _hash_eip191_message(structured_msg)
    expected_hex = '4e3c4173651b3054c0635dfae57a3b65ae1527ed0ba9ff76cecb6d9807687a7f'
    assert hashed_structured_msg.hex() == expected_hex


def test_signature_verification_eip712(eip712_message_encodings):
    account = Account.create()
    structured_msg = encode_structured_data(**eip712_message_encodings)
    signed = Account.sign_message(structured_msg, account.key)
    new_addr = Account.recover_message(structured_msg, signature=signed.signature)
    assert new_addr == account.address


def test_signature_verification_eip712_with_array(eip712_with_array_message_encodings):
    account = Account.create()
    structured_msg = encode_structured_data(**eip712_with_array_message_encodings)
    signed = Account.sign_message(structured_msg, account.key)
    new_addr = Account.recover_message(structured_msg, signature=signed.signature)
    assert new_addr == account.address


def test_signature_variables_eip712(eip712_message_encodings):
    # Check that the signature of typed message is the same as that
    # mentioned in the EIP. The link is as follows
    # https://github.com/ethereum/EIPs/blob/master/assets/eip-712/Example.js
    structured_msg = encode_structured_data(**eip712_message_encodings)

    private_key = keccak(text="cow")
    acc = Account.from_key(private_key)
    assert HexBytes(acc.address) == HexBytes("0xcd2a3d9f938e13cd947ec05abc7fe734df8dd826")

    sig = Account.sign_message(structured_msg, private_key)
    assert sig.v == 28
    assert hex(sig.r) == "0x4355c47d63924e8a72e509b65029052eb6c299d53a04e167c5775fd466751c9d"
    assert hex(sig.s) == "0x7299936d304c153f6443dfa05f40ff007d72911b6f72307f996231605b91562"


def test_signature_variables_eip712_with_array(eip712_with_array_message_encodings):
    structured_msg = encode_structured_data(**eip712_with_array_message_encodings)

    private_key = keccak(text="cow")
    acc = Account.from_key(private_key)
    assert HexBytes(acc.address) == HexBytes("0xcd2a3d9f938e13cd947ec05abc7fe734df8dd826")

    sig = Account.sign_message(structured_msg, private_key)
    assert sig.v == 27
    assert hex(sig.r) == "0x58635e9afd7a2a5338cf2af3d711b50235a1955c43f8bca1657c9d0834fcdb5a"
    assert hex(sig.s) == "0x44a7c0169616cfdfc16815714c9bc1c94139e17a0761a17530cf3dd1746bc10b"


def test_hashed_structured_data_with_bytes(eip712_example_with_array_json_string):
    structured_data = json.loads(eip712_example_with_array_json_string)

    # change 'contents' field to type ``bytes`` and set bytes value
    structured_data['types']['Mail'][3]['type'] = "bytes"
    structured_data['message']['contents'] = keccak(b'')

    structured_msg = encode_structured_data(structured_data)
    hashed_structured_msg = _hash_eip191_message(structured_msg)
    expected_hash_value_hex = "a06e87f57db20fed78428850bfe02a67d4c6c0f9bcb582b860299b21f591b1c6"
    assert hashed_structured_msg.hex() == expected_hash_value_hex


def test_hashed_structured_data_with_bytes32(eip712_example_with_array_json_string):
    structured_data = json.loads(eip712_example_with_array_json_string)

    # change 'contents' field to type ``bytes32`` and set bytes value
    structured_data['types']['Mail'][3]['type'] = "bytes32"
    structured_data['message']['contents'] = keccak(b'')

    structured_msg = encode_structured_data(structured_data)
    hashed_structured_msg = _hash_eip191_message(structured_msg)
    expected_hash_value_hex = "ff79c92bdd076a8ec12b146f82a278b30f4da5d402382e215abda4c3c186257e"
    assert hashed_structured_msg.hex() == expected_hash_value_hex


def test_hashed_structured_data_with_nested_structs():
    nested_structs_valid_data_json_string = open(
        "tests/fixtures/valid_message_nested_structs.json", "r"
    ).read()

    structured_data = json.loads(nested_structs_valid_data_json_string)
    structured_msg = encode_structured_data(structured_data)
    hashed_structured_msg = _hash_eip191_message(structured_msg)

    expected_hash_value_hex = "1a9c2ba3822f4f5498e4dfe3593ad69c9135a9f038334b49fa54537cfa9f5244"
    assert hashed_structured_msg.hex() == expected_hash_value_hex


@pytest.mark.parametrize(
    'type, valid',
    (
        ("unint bytes32", False),
        ("hello\\[]", False),
        ("byte[]uint", False),
        ("byte[7[]uint][]", False),
        ("Person[0]", False),

        ("bytes32", True),
        ("Foo[]", True),
        ("bytes1", True),
        ("bytes32[][][]", True),
        ("byte[9]", True),
        ("Person[1]", True),
    )
)
def test_type_regex(type, valid):
    if valid:
        assert re.match(TYPE_REGEX, type) is not None
    else:
        assert re.match(TYPE_REGEX, type) is None


def test_structured_data_invalid_identifier_filtered_by_regex():
    invalid_structured_data_string = open(
        "tests/fixtures/invalid_struct_identifier_message.json"
    ).read()
    with pytest.raises(ValidationError) as e:
        load_and_validate_structured_message(invalid_structured_data_string)
    assert str(e.value) == "Invalid Identifier `hello wallet` in `Person`"


def test_structured_data_invalid_type_filtered_by_regex():
    invalid_structured_data_string = open(
        "tests/fixtures/invalid_struct_type_message.json"
    ).read()
    with pytest.raises(ValidationError) as e:
        load_and_validate_structured_message(invalid_structured_data_string)
    assert str(e.value) == "Invalid Type `Hello Person` in `Mail`"


def test_invalid_structured_data_value_type_mismatch_in_primary_type():
    # Given type is valid (string), but the value (int) is not of the mentioned type
    invalid_structured_data_string = open(
        "tests/fixtures/invalid_message_value_type_mismatch_primary_type.json"
    ).read()
    invalid_structured_data = json.loads(invalid_structured_data_string)

    with pytest.raises(
        TypeError,
        match="in the struct `Mail` is of the type `<class 'int'>`, but expected string value"
    ):
        hash_message(invalid_structured_data)


def test_invalid_structured_data_invalid_abi_type():
    # Given type/types are invalid
    invalid_structured_data_string = open(
        "tests/fixtures/invalid_message_invalid_abi_type.json"
    ).read()
    invalid_structured_data = json.loads(invalid_structured_data_string)
    with pytest.raises(TypeError, match="Received Invalid type `uint25689` in the struct `Person`"):
        hash_message(invalid_structured_data)


def test_structured_data_invalid_identifier_filtered_by_abi_encodable_function():
    # Given valid abi type, but the value is not encodable as the specified type
    # (Error is found by the ``is_encodable`` ABI function)
    invalid_structured_data_string = open(
        "tests/fixtures/invalid_message_valid_abi_type_invalid_value.json"
    ).read()
    invalid_structured_data = json.loads(invalid_structured_data_string)
    with pytest.raises(TypeError) as e:
        hash_message(invalid_structured_data)
    assert (
        str(e.value) == "Value of `balance` (how do you do?) in the struct `Person` is not "
                        "encodable as the specified type `uint256`. If the base type is correct, "
                        "make sure the value does not exceed the specified size for the type."
    )


@pytest.mark.parametrize(
    'data, expected',
    (
        ([[1, 2, 3], [4, 5, 6]], (2, 3)),
        ([[1, 2, 3]], (1, 3)),
        ([1, 2, 3], (3,)),
        ([[[1, 2], [3, 4], [5, 6]], [[7, 8], [9, 10], [11, 12]]], (2, 3, 2)),
    )
)
def test_get_array_dimensions(data, expected):
    assert get_array_dimensions(data) == expected


def test_unequal_array_lengths_between_schema_and_data():
    invalid_structured_data_string = open(
        "tests/fixtures/invalid_message_unequal_1d_array_lengths.json"
    ).read()
    invalid_structured_data = json.loads(invalid_structured_data_string)
    with pytest.raises(TypeError) as e:
        hash_message(invalid_structured_data)
    assert (
        str(e.value) == (
            "Array data "
            "`[{'name': 'Bob', 'wallet': '0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB'}]` has "
            "dimensions `(1,)` whereas the schema has dimensions `(2,)`"
        ) or str(e.value) == (
            "Array data "
            "`[{'wallet': '0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB', 'name': 'Bob'}]` has "
            "dimensions `(1,)` whereas the schema has dimensions `(2,)`"
        )
    )


def test_unequal_array_dimension_between_schema_and_data():
    invalid_structured_data_string = open(
        "tests/fixtures/invalid_message_unequal_array_dimensions.json"
    ).read()
    invalid_structured_data = json.loads(invalid_structured_data_string)
    with pytest.raises(TypeError) as e:
        hash_message(invalid_structured_data)
    assert (
        str(e.value) == (
            "Array data "
            "`[{'name': 'Bob', 'wallet': '0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB'}]` has "
            "dimensions `(1,)` whereas the schema has dimensions `(2, 3, 4)`"
        ) or str(e.value) == (
            "Array data "
            "`[{'wallet': '0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB', 'name': 'Bob'}]` has "
            "dimensions `(1,)` whereas the schema has dimensions `(2, 3, 4)`"
        )
    )
