import json
import pytest
import re
import time

from eth_abi.exceptions import (
    ABITypeError,
)
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
def structured_valid_data_json_string():
    return open("tests/fixtures/valid_message.json", "r").read()


@pytest.fixture
def types(structured_valid_data_json_string):
    return json.loads(structured_valid_data_json_string)["types"]


@pytest.fixture
def domain_type(structured_valid_data_json_string):
    return json.loads(structured_valid_data_json_string)["types"]["EIP712Domain"]


@pytest.fixture
def message(structured_valid_data_json_string):
    return json.loads(structured_valid_data_json_string)["message"]


@pytest.fixture
def domain(structured_valid_data_json_string):
    return json.loads(structured_valid_data_json_string)["domain"]


@pytest.fixture(params=("text", "dict", "primitive", "hexstr"))
def message_encodings(request, structured_valid_data_json_string):
    if request.param == "text":
        return {"text": structured_valid_data_json_string}
    elif request.param == "primitive":
        return {"primitive": structured_valid_data_json_string.encode()}
    elif request.param == "dict":
        return {"primitive": json.loads(structured_valid_data_json_string)}
    elif request.param == "hexstr":
        return {"hexstr": structured_valid_data_json_string.encode().hex()}
    else:
        raise Exception("Unreachable")


@pytest.mark.parametrize(
    'primary_type, expected',
    (
        ('Mail', ('Person',)),
        ('Person', ()),
    )
)
def test_get_dependencies(primary_type, types, expected):
    assert get_dependencies(primary_type, types) == expected


@pytest.mark.parametrize(
    'struct_name, expected',
    (
        ("Mail", "Mail(Person from,Person to,Person[] cc,string contents)"),
        ("Person", "Person(string name,address wallet)"),
        ("EIP712Domain", (
            "EIP712Domain(string name,string version,"
            "uint256 chainId,address verifyingContract)"
        )),
    )
)
def test_encode_struct(struct_name, types, expected):
    assert encode_struct(struct_name, types[struct_name]) == expected


@pytest.mark.parametrize(
    'primary_type, expected',
    (
        ('Mail', 'Mail(Person from,Person to,Person[] cc,string contents)Person(string name,address wallet)'),  # noqa: E501
        ('Person', 'Person(string name,address wallet)'),
    )
)
def test_encode_type(primary_type, types, expected):
    assert encode_type(primary_type, types) == expected


@pytest.mark.parametrize(
    'primary_type, expected_hex_value',
    (
        ('Mail', 'b19c5c7781083ed7325660d847f8c547b744917d67b38858b00bce7e62a4866b'),
        ('Person', 'b9d8c78acf9b987311de6c7b45bb6a9c8e1bf361fa7fd3467a2163f994c79500'),
    )
)
def test_hash_struct_type(primary_type, types, expected_hex_value):
    assert hash_struct_type(primary_type, types).hex() == expected_hex_value


def test_encode_data(types, message):
    primary_type = "Mail"
    expected_hex_value = (
        "b19c5c7781083ed7325660d847f8c547b744917d67b38858b00bce7e62a4866bfc71e5fa27ff56c350aa531bc1"
        "29ebdf613b772b6604664f5d8dbe21b85eb0c8cd54f074a4af31b4411ff6a60c9719dbd559c221c8ac3492d9d8"
        "72b041d703d1a88b5e35e8f6bccc3d72ef467ed581615888f8cf34df19d068d04225439be65ab5aadf3154a261"
        "abdd9086fc627b61efca26ae5702701d05cd2305f7c52a2fc8"
    )
    assert encode_data(primary_type, types, message).hex() == expected_hex_value


def test_hash_struct_main_message(structured_valid_data_json_string):
    structured_data = json.loads(structured_valid_data_json_string)
    expected_hex_value = "76649452daa3e4101beef5b01669fd0de45ece35188d529703c73526a2454521"
    assert hash_message(structured_data).hex() == expected_hex_value


def test_hash_struct_domain(structured_valid_data_json_string):
    structured_data = json.loads(structured_valid_data_json_string)
    expected_hex_value = "f2cee375fa42b42143804025fc449deafd50cc031ca257e0b194a650a912090f"
    assert hash_domain(structured_data).hex() == expected_hex_value


def test_hashed_structured_data(message_encodings):
    structured_msg = encode_structured_data(**message_encodings)
    hashed_structured_msg = _hash_eip191_message(structured_msg)
    expected_hash_value_hex = "4e3c4173651b3054c0635dfae57a3b65ae1527ed0ba9ff76cecb6d9807687a7f"
    assert hashed_structured_msg.hex() == expected_hash_value_hex


def test_signature_verification(message_encodings):
    account = Account.create()
    structured_msg = encode_structured_data(**message_encodings)
    signed = Account.sign_message(structured_msg, account.key)
    new_addr = Account.recover_message(structured_msg, signature=signed.signature)
    assert new_addr == account.address


def test_signature_variables(message_encodings):
    # Check that the signature of typed message is the same as that
    # mentioned in the EIP. The link is as follows
    # https://github.com/ethereum/EIPs/blob/master/assets/eip-712/Example.js
    structured_msg = encode_structured_data(**message_encodings)
    privateKey = keccak(text="cow")
    acc = Account.from_key(privateKey)
    assert HexBytes(acc.address) == HexBytes("0xcd2a3d9f938e13cd947ec05abc7fe734df8dd826")
    sig = Account.sign_message(structured_msg, privateKey)
    assert sig.v == 27
    assert hex(sig.r) == "0x58635e9afd7a2a5338cf2af3d711b50235a1955c43f8bca1657c9d0834fcdb5a"
    assert hex(sig.s) == "0x44a7c0169616cfdfc16815714c9bc1c94139e17a0761a17530cf3dd1746bc10b"


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


def test_type_regex_for_redos():
    start = time.time()
    # len 30 string is long enough to cause > 1 second delay if the regex is bad
    long = '1' * 30
    invalid_structured_data_string = f"""{{
        "types": {{
            "EIP712Domain": [
                {{"name": "aaaa", "type": "$[{long}0"}},
                {{"name": "version", "type": "string"}},
                {{"name": "chainId", "type": "uint256"}},
                {{"name": "verifyingContract", "type": "address"}}
            ]
        }}
    }}"""

    with pytest.raises(re.error, match="unterminated character set at position 15"):
        with pytest.raises(ValidationError, match=f"Invalid Type `$[{long}0` in `EIP712Domain`"):
            load_and_validate_structured_message(invalid_structured_data_string)

    done = time.time() - start
    assert done < 1


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
    with pytest.raises(TypeError) as e:
        hash_message(invalid_structured_data)
    assert (
        str(e.value) == "Value of `contents` (12345) in the struct `Mail` is of the "
        "type `<class 'int'>`, but expected string value"
    )


def test_invalid_structured_data_invalid_abi_type():
    # Given type/types are invalid
    invalid_structured_data_string = open(
        "tests/fixtures/invalid_message_invalid_abi_type.json"
    ).read()
    invalid_structured_data = json.loads(invalid_structured_data_string)
    with pytest.raises(ABITypeError) as e:
        hash_message(invalid_structured_data)
    assert "'uint25689': integer size out of bounds" in str(e.value)


def test_structured_data_invalid_identifier_filtered_by_abi_encodable_function():
    # Given valid abi type, but the value is not of the specified type
    # (Error is found by the ``is_encodable`` ABI function)
    invalid_structured_data_string = open(
        "tests/fixtures/invalid_message_valid_abi_type_invalid_value.json"
    ).read()
    invalid_structured_data = json.loads(invalid_structured_data_string)
    with pytest.raises(TypeError) as e:
        hash_message(invalid_structured_data)
    assert (
        str(e.value) == "Value of `balance` (how do you do?) in the struct `Person` is of the "
        "type `<class 'str'>`, but expected uint256 value"
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
