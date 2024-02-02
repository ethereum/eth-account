from copy import (
    deepcopy,
)
import json
import re
import time

from eth_utils import (
    ValidationError,
    keccak,
)
from hexbytes import (
    HexBytes,
)
import pytest

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
    return open("tests/fixtures/valid_eip712_example.json").read()


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
    return open("tests/fixtures/valid_eip712_example_with_array.json").read()


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


# --- EIP 712 example with added multiple array fields --- #


@pytest.fixture
def eip712_example_with_multi_array_json_string():
    return open("tests/fixtures/valid_eip712_example_with_multi_array.json").read()


@pytest.fixture
def eip712_example_with_multi_array_types(eip712_example_with_multi_array_json_string):
    return json.loads(eip712_example_with_multi_array_json_string)["types"]


@pytest.fixture
def eip712_example_with_multi_array_domain_type(
    eip712_example_with_multi_array_json_string,
):
    return json.loads(eip712_example_with_multi_array_json_string)["types"][
        "EIP712Domain"
    ]


@pytest.fixture
def eip712_example_with_multi_array_message(
    eip712_example_with_multi_array_json_string,
):
    return json.loads(eip712_example_with_multi_array_json_string)["message"]


@pytest.fixture
def eip712_example_with_multi_array_domain(eip712_example_with_multi_array_json_string):
    return json.loads(eip712_example_with_multi_array_json_string)["domain"]


@pytest.fixture(params=("text", "dict", "primitive", "hexstr"))
def eip712_with_multi_array_message_encodings(
    request, eip712_example_with_multi_array_json_string
):
    if request.param == "text":
        return {"text": eip712_example_with_multi_array_json_string}
    elif request.param == "primitive":
        return {"primitive": eip712_example_with_multi_array_json_string.encode()}
    elif request.param == "dict":
        return {"primitive": json.loads(eip712_example_with_multi_array_json_string)}
    elif request.param == "hexstr":
        return {"hexstr": eip712_example_with_multi_array_json_string.encode().hex()}
    else:
        raise Exception("Unreachable")


@pytest.mark.parametrize(
    "primary_type, types, eip712_data, expected_hex",
    (
        (
            "BoolInt",
            {
                "BoolInt": [
                    {"name": "bool", "type": "bool"},
                    {"name": "bool_a", "type": "bool[]"},
                    {"name": "int", "type": "uint256"},
                    {"name": "int_a", "type": "uint256[][3]"},
                ]
            },
            {
                "bool": True,
                "bool_a": [False, True],
                "int": 212,
                "int_a": [[212], [], [12, 24, 36]],
            },
            "8d06a59c4f3179fc688615a1d69d61ee86c9683a5c3af150874396b3021892200000000000"
            "000000000000000000000000000000000000000000000000000001a6eef7e35abe70267296"
            "41147f7915573c7e97b47efa546f5f6e3230263bcb49000000000000000000000000000000"
            "00000000000000000000000000000000d4eb11d95b7e83141a4db340518d5fc187abde6f73"
            "e97cb1a5c7854c23c8cdf8fa",
        ),
        (
            "StringBytes",
            {
                "StringBytes": [
                    {"name": "string", "type": "string"},
                    {"name": "string_a", "type": "string[]"},
                    {"name": "bytes", "type": "bytes"},
                    {"name": "bytes_a", "type": "bytes[]"},
                ]
            },
            {
                "string": "spam",
                "string_a": ["spam", "eggs"],
                "bytes": b"snekshak",
                "bytes_a": [b"shake", b"snake"],
            },
            "763a70467632fd4d114a365d4f03c5886ce9447950874f45cbd42421cbc5f17d"
            "000e3bc84207015e1ae7e42b8679963a82088323f7ef1b456c44eda274f579f6"
            "3b78c672c715dfcb45484f0c5a488c1a20679e7e4ec1d980f43165671b70a3e4"
            "9079dbeec4d62f4344389883b7fe5fcedc73483b9d6a4774ab0857bedd7dd14d"
            "7578ae1ed519e90d30b2e031348369679d8c09f47f717eb17de4bce1a7ad5d6b",
        ),
    ),
)
def test_encode_data_basic(primary_type, types, eip712_data, expected_hex):
    assert encode_data(primary_type, types, eip712_data).hex() == expected_hex


@pytest.mark.parametrize(
    "primary_type, types, eip712_data, error_type, error_message",
    (
        (
            "Missing",
            {
                "Missing": [
                    {"name": "bool", "type": "bool"},
                ]
            },
            {
                "bool": None,
            },
            ValueError,
            "Missing value for field bool of type bool",
        ),
        (
            "NotBytes",
            {
                "NotBytes": [
                    {"name": "bytes", "type": "bytes"},
                ]
            },
            {
                "bytes": 212,
            },
            TypeError,
            "Value of field `bytes` (212) is of the type `<class 'int'>`, "
            "but expected bytes value",
        ),
        (
            "NotString",
            {
                "NotString": [
                    {"name": "string", "type": "string"},
                ]
            },
            {
                "string": b"snakes",
            },
            TypeError,
            "Value of field `string` (b'snakes') is of the type `<class 'bytes'>`, "
            "but expected string value",
        ),
        (
            "NotEncodableType",
            {
                "NotEncodableType": [
                    {"name": "wat", "type": "wat"},
                ]
            },
            {
                "wat": "huh",
            },
            TypeError,
            "Received Invalid type `wat` in field `wat`",
        ),
        (
            "NotEncodableAsType",
            {
                "NotEncodableAsType": [
                    {"name": "wat", "type": "uint256"},
                ]
            },
            {
                "wat": True,
            },
            TypeError,
            "Value of `wat` (True) is not encodable as type `uint256`. "
            "If the base type is correct, verify that the value does not "
            "exceed the specified size for the type.",
        ),
    ),
)
def test_encode_data_error_messages(
    primary_type, types, eip712_data, error_type, error_message
):
    with pytest.raises(error_type) as e:
        assert encode_data(primary_type, types, eip712_data)
    assert str(e.value) == error_message


@pytest.mark.parametrize(
    "primary_type, expected",
    (
        ("Mail", ("Person",)),
        ("Person", ()),
    ),
)
def test_get_dependencies_eip712(primary_type, expected, eip712_example_types):
    assert get_dependencies(primary_type, eip712_example_types) == expected


@pytest.mark.parametrize(
    "primary_type, expected",
    (
        ("Mail", ("Person",)),
        ("Person", ()),
    ),
)
def test_get_dependencies_eip712_with_array(
    primary_type, expected, eip712_example_with_array_types
):
    assert get_dependencies(primary_type, eip712_example_with_array_types) == expected


@pytest.mark.parametrize(
    "primary_type, expected",
    (
        ("Mail", ("Person", "Company")),
        ("Person", ("Company",)),
        ("Company", ()),
    ),
)
def test_get_dependencies_eip712_with_multi_array(
    primary_type, expected, eip712_example_with_multi_array_types
):
    assert set(
        get_dependencies(primary_type, eip712_example_with_multi_array_types)
    ) == set(expected)


@pytest.mark.parametrize(
    "struct_name, expected",
    (
        ("Mail", "Mail(Person from,Person to,string contents)"),
        ("Person", "Person(string name,address wallet)"),
        (
            "EIP712Domain",
            "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)",  # noqa: E501
        ),
    ),
)
def test_encode_struct_eip712(struct_name, expected, eip712_example_types):
    assert encode_struct(struct_name, eip712_example_types[struct_name]) == expected


@pytest.mark.parametrize(
    "struct_name, expected",
    (
        ("Mail", "Mail(Person from,Person to,Person[] cc,string contents)"),
        ("Person", "Person(string name,address wallet)"),
        (
            "EIP712Domain",
            "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)",  # noqa: E501
        ),
    ),
)
def test_encode_struct_eip712_with_array(
    struct_name, expected, eip712_example_with_array_types
):
    assert (
        encode_struct(struct_name, eip712_example_with_array_types[struct_name])
        == expected
    )


@pytest.mark.parametrize(
    "struct_name, expected",
    (
        (
            "Mail",
            "Mail(uint256[] ids,Person from,Person to,Person[] cc,Person[][] bcc,string contents,string[3][4][2] tags)",  # noqa: E501
        ),
        (
            "Person",
            "Person(string name,Company company,string[] aliases,address wallet)",
        ),
        ("Company", "Company(string name,uint256 id)"),
        (
            "EIP712Domain",
            "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)",  # noqa: E501
        ),
    ),
)
def test_encode_struct_eip712_with_multi_array(
    struct_name, expected, eip712_example_with_multi_array_types
):
    assert (
        encode_struct(struct_name, eip712_example_with_multi_array_types[struct_name])
        == expected
    )


@pytest.mark.parametrize(
    "primary_type, expected",
    (
        (
            "Mail",
            "Mail(Person from,Person to,string contents)Person(string name,address wallet)",  # noqa: E501
        ),
        ("Person", "Person(string name,address wallet)"),
    ),
)
def test_encode_type_eip712(primary_type, expected, eip712_example_types):
    assert encode_type(primary_type, eip712_example_types) == expected


@pytest.mark.parametrize(
    "primary_type, expected",
    (
        (
            "Mail",
            "Mail(Person from,Person to,Person[] cc,string contents)Person(string name,address wallet)",  # noqa: E501
        ),
        ("Person", "Person(string name,address wallet)"),
    ),
)
def test_encode_type_eip712_with_array(
    primary_type, expected, eip712_example_with_array_types
):
    assert encode_type(primary_type, eip712_example_with_array_types) == expected


@pytest.mark.parametrize(
    "primary_type, expected",
    (
        (
            "Mail",
            "Mail(uint256[] ids,Person from,Person to,Person[] cc,Person[][] bcc,string contents,string[3][4][2] tags)Company(string name,uint256 id)Person(string name,Company company,string[] aliases,address wallet)",  # noqa: E501
        ),
        (
            "Person",
            "Person(string name,Company company,string[] aliases,address wallet)Company(string name,uint256 id)",  # noqa: E501
        ),
        ("Company", "Company(string name,uint256 id)"),
    ),
)
def test_encode_type_eip712_with_multi_array(
    primary_type, expected, eip712_example_with_multi_array_types
):
    assert encode_type(primary_type, eip712_example_with_multi_array_types) == expected


@pytest.mark.parametrize(
    "primary_type, expected_hex",
    (
        ("Mail", "a0cedeb2dc280ba39b857546d74f5549c3a1d7bdc2dd96bf881f76108e23dac2"),
        ("Person", "b9d8c78acf9b987311de6c7b45bb6a9c8e1bf361fa7fd3467a2163f994c79500"),
    ),
)
def test_hash_struct_type_eip712(primary_type, expected_hex, eip712_example_types):
    assert hash_struct_type(primary_type, eip712_example_types).hex() == expected_hex


@pytest.mark.parametrize(
    "primary_type, expected_hex",
    (
        ("Person", "b9d8c78acf9b987311de6c7b45bb6a9c8e1bf361fa7fd3467a2163f994c79500"),
        ("Mail", "b19c5c7781083ed7325660d847f8c547b744917d67b38858b00bce7e62a4866b"),
    ),
)
def test_hash_struct_type_eip712_with_array(
    primary_type, expected_hex, eip712_example_with_array_types
):
    assert (
        hash_struct_type(primary_type, eip712_example_with_array_types).hex()
        == expected_hex
    )


@pytest.mark.parametrize(
    "primary_type, expected_hex",
    (
        ("Company", "6ca77e7c32d0c89b799964b908f09a67d27441f2c23a6fb1fe12744a6ad629f7"),
        ("Person", "c7b964db9fb195cb39c83204fdf1f0f406b6a2f3e463db9cad34aa0c040380a9"),
        ("Mail", "1cf41a63c532d5c0c81650d839a38629cc2ab400a6a4bd000b4188adf9dd7540"),
    ),
)
def test_hash_struct_type_eip712_with_multi_array(
    primary_type, expected_hex, eip712_example_with_multi_array_types
):
    assert (
        hash_struct_type(primary_type, eip712_example_with_multi_array_types).hex()
        == expected_hex
    )


def test_encode_data_eip712(eip712_example_types, eip712_example_message):
    primary_type = "Mail"
    expected_hex = (
        "a0cedeb2dc280ba39b857546d74f5549c3a1d7bdc2dd96bf881f76108e23dac2fc71e5fa27ff"
        "56c350aa531bc129ebdf613b772b6604664f5d8dbe21b85eb0c8cd54f074a4af31b4411ff6a6"
        "0c9719dbd559c221c8ac3492d9d872b041d703d1b5aadf3154a261abdd9086fc627b61efca26"
        "ae5702701d05cd2305f7c52a2fc8"
    )
    assert (
        encode_data(primary_type, eip712_example_types, eip712_example_message).hex()
        == expected_hex
    )


def test_encode_data_eip712_with_array(
    eip712_example_with_array_types, eip712_example_with_array_message
):
    primary_type = "Mail"
    expected_hex = (
        "b19c5c7781083ed7325660d847f8c547b744917d67b38858b00bce7e62a4866bfc71e5fa27ff"
        "56c350aa531bc129ebdf613b772b6604664f5d8dbe21b85eb0c8cd54f074a4af31b4411ff6a6"
        "0c9719dbd559c221c8ac3492d9d872b041d703d105a7f44bc01de4515b63df31009d8ce4fe8b"
        "06eb06a1ff4eec0b562d1c703535b5aadf3154a261abdd9086fc627b61efca26ae5702701d05"
        "cd2305f7c52a2fc8"
    )
    assert (
        encode_data(
            primary_type,
            eip712_example_with_array_types,
            eip712_example_with_array_message,
        ).hex()
        == expected_hex
    )


def test_encode_data_eip712_with_multi_array(
    eip712_example_with_multi_array_types, eip712_example_with_multi_array_message
):
    primary_type = "Mail"
    expected_hex = (
        "1cf41a63c532d5c0c81650d839a38629cc2ab400a6a4bd000b4188adf9dd754082ebb1c2e604ce"
        "0ff44d8591ae5cf16cbafd622284d40b37011b12dca2e2d9e4a30aec196a390f2dc9de7320f587"
        "4214e5a7929e08a7a81d9ef96666fdcbab35e1f45419ba2d57832f702e17b344e470f556cda74e"
        "91e703303656404b77fec1c6c072aa6915cd93401ec3be997eedadb9bb3f6300ab5c9e61808efa"
        "bf7da54687a9c71c4a727b1ca222ac101d1fc58980c48ad66baac15c14a68bbaaced314fb5aadf"
        "3154a261abdd9086fc627b61efca26ae5702701d05cd2305f7c52a2fc888e7f5caefc6a01fd300"
        "aaa708d99f8c04ed97879c2fc16950cb82957ff79099"
    )
    assert (
        encode_data(
            primary_type,
            eip712_example_with_multi_array_types,
            eip712_example_with_multi_array_message,
        ).hex()
        == expected_hex
    )


def test_hash_struct_main_message_eip712(eip712_example_json_string):
    structured_data = json.loads(eip712_example_json_string)
    expected_hex = "c52c0ee5d84264471806290a3f2c4cecfc5490626bf912d01f240d7a274b371e"
    assert hash_message(structured_data).hex() == expected_hex


def test_hash_struct_main_message_eip712_with_array(
    eip712_example_with_array_json_string,
):
    structured_data = json.loads(eip712_example_with_array_json_string)
    expected_hex = "04e58c373e4cd0695f0c2d6e2d8e379d6b51b987cf27d582dd94a03532d430d3"
    assert hash_message(structured_data).hex() == expected_hex


def test_hash_struct_main_message_eip712_with_multi_array(
    eip712_example_with_multi_array_json_string,
):  # noqa: E501
    structured_data = json.loads(eip712_example_with_multi_array_json_string)
    expected_hex = "6c5faac29b3f4552147e5cfef75b4ac09fdc7668ba1208c5f153f047a0da4819"
    assert hash_message(structured_data).hex() == expected_hex


def test_hash_struct_domain_eip712(eip712_example_json_string):
    structured_data = json.loads(eip712_example_json_string)
    expected_hex = "f2cee375fa42b42143804025fc449deafd50cc031ca257e0b194a650a912090f"
    assert hash_domain(structured_data).hex() == expected_hex


def test_hash_struct_domain_eip712_with_array(eip712_example_with_array_json_string):
    structured_data = json.loads(eip712_example_with_array_json_string)
    expected_hex = "f2cee375fa42b42143804025fc449deafd50cc031ca257e0b194a650a912090f"
    assert hash_domain(structured_data).hex() == expected_hex


def test_hash_struct_domain_eip712_with_multi_array(
    eip712_example_with_multi_array_json_string,
):
    structured_data = json.loads(eip712_example_with_multi_array_json_string)
    expected_hex = "f2cee375fa42b42143804025fc449deafd50cc031ca257e0b194a650a912090f"
    assert hash_domain(structured_data).hex() == expected_hex


def test_hashed_structured_data_eip712(eip712_message_encodings):
    structured_msg = encode_structured_data(**eip712_message_encodings)
    hashed_structured_msg = _hash_eip191_message(structured_msg)
    expected_hex = "be609aee343fb3c4b28e1df9e632fca64fcfaede20f02e86244efddf30957bd2"
    assert hashed_structured_msg.hex() == expected_hex


def test_hashed_structured_data_eip712_with_array(eip712_with_array_message_encodings):
    structured_msg = encode_structured_data(**eip712_with_array_message_encodings)
    hashed_structured_msg = _hash_eip191_message(structured_msg)
    expected_hex = "1780e7e042fa9ec126ccb68cd707d61580d00601b3eff8a5ec05116b46007fdb"
    assert hashed_structured_msg.hex() == expected_hex


def test_hashed_structured_data_eip712_with_multi_array(
    eip712_with_multi_array_message_encodings,
):
    structured_msg = encode_structured_data(**eip712_with_multi_array_message_encodings)
    hashed_structured_msg = _hash_eip191_message(structured_msg)
    expected_hex = "da275374c3a0790d389b6490d6fdf499f39c72105423f09d7b9be62d2fc08671"
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


def test_signature_verification_eip712_with_multi_array(
    eip712_with_multi_array_message_encodings,
):
    account = Account.create()
    structured_msg = encode_structured_data(**eip712_with_multi_array_message_encodings)
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
    assert HexBytes(acc.address) == HexBytes(
        "0xcd2a3d9f938e13cd947ec05abc7fe734df8dd826"
    )

    sig = Account.sign_message(structured_msg, private_key)
    assert sig.v == 28
    assert (
        hex(sig.r)
        == "0x4355c47d63924e8a72e509b65029052eb6c299d53a04e167c5775fd466751c9d"
    )
    assert (
        hex(sig.s)
        == "0x7299936d304c153f6443dfa05f40ff007d72911b6f72307f996231605b91562"
    )


def test_signature_variables_eip712_with_array(eip712_with_array_message_encodings):
    structured_msg = encode_structured_data(**eip712_with_array_message_encodings)

    private_key = keccak(text="cow")
    acc = Account.from_key(private_key)
    assert HexBytes(acc.address) == HexBytes(
        "0xcd2a3d9f938e13cd947ec05abc7fe734df8dd826"
    )

    sig = Account.sign_message(structured_msg, private_key)
    assert sig.v == 27
    assert (
        hex(sig.r)
        == "0x315bd45341016e306aa54a7aaf002104b7a5b51903be6ca04cef9d49555319f1"
    )
    assert (
        hex(sig.s)
        == "0x46afff92b3504a3ab106dd96c414e38709515d884433816801ddde8d10136c8c"
    )


def test_signature_variables_eip712_with_multi_array(
    eip712_with_multi_array_message_encodings,
):
    structured_msg = encode_structured_data(**eip712_with_multi_array_message_encodings)

    private_key = keccak(text="cow")
    acc = Account.from_key(private_key)
    assert HexBytes(acc.address) == HexBytes(
        "0xcd2a3d9f938e13cd947ec05abc7fe734df8dd826"
    )

    sig = Account.sign_message(structured_msg, private_key)
    assert sig.v == 27
    assert (
        hex(sig.r)
        == "0x873be7f5ac9688ea3675b0c44916340883103053de9d1f9d0c1b6e9758a78a2b"
    )
    assert (
        hex(sig.s)
        == "0x6309769ff21b7a4f610316b249b004d4f9e9e9d6df2634d9bc0f492cda6b9c06"
    )


def test_hashed_structured_data_with_bytes(eip712_example_with_array_json_string):
    structured_data = json.loads(eip712_example_with_array_json_string)

    # change 'contents' field to type ``bytes`` and set bytes value
    structured_data["types"]["Mail"][3]["type"] = "bytes"
    structured_data["message"]["contents"] = keccak(b"")

    structured_msg = encode_structured_data(structured_data)
    hashed_structured_msg = _hash_eip191_message(structured_msg)
    expected_hash_value_hex = (
        "6de2148c1b98a586b42eaac9bbd72c4af5ee490fc1ec53fe483667c8fb38d10d"
    )
    assert hashed_structured_msg.hex() == expected_hash_value_hex


def test_hashed_structured_data_with_bytes32(eip712_example_with_array_json_string):
    structured_data = json.loads(eip712_example_with_array_json_string)

    # change 'contents' field to type ``bytes32`` and set bytes value
    structured_data["types"]["Mail"][3]["type"] = "bytes32"
    structured_data["message"]["contents"] = keccak(b"")

    structured_msg = encode_structured_data(structured_data)
    hashed_structured_msg = _hash_eip191_message(structured_msg)
    expected_hash_value_hex = (
        "c9f862d796deff552a90d7de1faff9a4b7f99726bf7518dc00073d23373d0530"
    )
    assert hashed_structured_msg.hex() == expected_hash_value_hex


def test_hashed_structured_data_with_nested_structs():
    nested_structs_valid_data_json_string = open(
        "tests/fixtures/valid_message_nested_structs.json"
    ).read()

    structured_data = json.loads(nested_structs_valid_data_json_string)
    structured_msg = encode_structured_data(structured_data)
    hashed_structured_msg = _hash_eip191_message(structured_msg)

    expected_hash_value_hex = (
        "0c9b68928afbff5af30e99ae29fcdf1cc36974f7ba4a6e4336cc98daa4f0c2af"
    )
    assert hashed_structured_msg.hex() == expected_hash_value_hex


@pytest.mark.parametrize(
    "type, valid",
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
    ),
)
def test_type_regex(type, valid):
    if valid:
        assert re.match(TYPE_REGEX, type) is not None
    else:
        assert re.match(TYPE_REGEX, type) is None


def test_type_regex_for_redos():
    start = time.time()
    # len 30 string is long enough to cause > 1 second delay if the regex is bad
    long = "1" * 30
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
        with pytest.raises(
            ValidationError, match=f"Invalid Type `$[{long}0` in `EIP712Domain`"
        ):
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


def test_invalid_structured_data_value_type_mismatch_in_type():
    # Given type is valid (string), but the value (int) is not of the mentioned type
    invalid_structured_data_string = open(
        "tests/fixtures/invalid_message_value_type_mismatch_type.json"
    ).read()
    invalid_structured_data = json.loads(invalid_structured_data_string)
    with pytest.raises(
        TypeError,
        match="Value of field `contents` \\(12345\\) is of the type `<class 'int'>`, "
        "but expected string value",
    ):
        hash_message(invalid_structured_data)


def test_invalid_structured_data_invalid_abi_type():
    # Given type/types are invalid
    invalid_structured_data_string = open(
        "tests/fixtures/invalid_message_invalid_abi_type.json"
    ).read()
    invalid_structured_data = json.loads(invalid_structured_data_string)
    with pytest.raises(
        TypeError, match="Received Invalid type `uint25689` in field `balance`"
    ):
        hash_message(invalid_structured_data)


def test_structured_data_invalid_identifier_filtered_by_abi_encodable_function():
    # Given valid abi type, but the value is not encodable as the specified type
    # (Error is found by the ``is_encodable`` ABI function)
    invalid_structured_data_string = open(
        "tests/fixtures/invalid_message_valid_abi_type_invalid_value.json"
    ).read()
    invalid_structured_data = json.loads(invalid_structured_data_string)
    with pytest.raises(
        TypeError,
        match="Value of `balance` \\(how do you do\\?\\) is not encodable as type "
        "`uint256`. If the base type is correct, verify that the "
        "value does not exceed the specified size for the type.",
    ):
        hash_message(invalid_structured_data)


@pytest.mark.parametrize(
    "data, expected",
    (
        ([[1, 2, 3], [4, 5, 6]], (3, 2)),
        ([[1, 2, 3]], (3, 1)),
        ([1, 2, 3], (3,)),
        ([[[1, 2], [3, 4], [5, 6]], [[7, 8], [9, 10], [11, 12]]], (2, 3, 2)),
        # test dynamic when varying array sizes exist within the same dimension
        ([[212], [], [12, 24, 36]], ("dynamic", 3)),
        ([[212], [], [12, [22, 24], [36]]], ("dynamic", "dynamic", 3)),
    ),
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
    assert str(e.value) == (
        "Array data "
        "`[{'name': 'Bob', 'wallet': '0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB'}]` "
        "has dimensions `(1,)` whereas the schema has dimensions `(2,)`"
    ) or str(e.value) == (
        "Array data "
        "`[{'wallet': '0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB', 'name': 'Bob'}]` "
        "has dimensions `(1,)` whereas the schema has dimensions `(2,)`"
    )


def test_unequal_array_dimension_between_schema_and_data():
    invalid_structured_data_string = open(
        "tests/fixtures/invalid_message_unequal_array_dimensions.json"
    ).read()
    invalid_structured_data = json.loads(invalid_structured_data_string)
    with pytest.raises(TypeError) as e:
        hash_message(invalid_structured_data)
    assert str(e.value) == (
        "Array data "
        "`[{'name': 'Bob', 'wallet': '0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB'}]` "
        "has dimensions `(1,)` whereas the schema has dimensions `(2, 'dynamic', 4)`"
    ) or str(e.value) == (
        "Array data "
        "`[{'wallet': '0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB', 'name': 'Bob'}]` "
        "has dimensions `(1,)` whereas the schema has dimensions `(2, 'dynamic', 4)`"
    )


def test_encode_structured_data_ignores_additional_data_in_a_custom_type():
    message_with_additonal_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
            ],
            "Person": [
                {"name": "name", "type": "string"},
            ],
        },
        "primaryType": "Person",
        "domain": {
            "name": "Name",
        },
        "message": {
            "name": "Bob",
            "pet": {
                "animal": "cat",
                "age": 3,
            },
        },
    }

    message_without_additonal_data = deepcopy(message_with_additonal_data)
    message_without_additonal_data["message"].pop("pet")
    assert message_without_additonal_data["message"].get("pet") is None

    assert encode_structured_data(
        message_with_additonal_data
    ) == encode_structured_data(message_without_additonal_data)


def test_encode_typed_data_ignores_unused_types():
    message_with_unused_type = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
            ],
            "Person": [
                {"name": "name", "type": "string"},
            ],
            "OtherPerson": [
                {"name": "name", "type": "string"},
            ],
        },
        "primaryType": "Person",
        "domain": {
            "name": "Name",
        },
        "message": {
            "name": "Bob",
        },
    }

    message_without_unused_type = deepcopy(message_with_unused_type)
    message_without_unused_type["types"].pop("OtherPerson")
    assert message_without_unused_type["types"].get("OtherPerson") is None

    assert encode_structured_data(message_with_unused_type) == encode_structured_data(
        message_without_unused_type
    )


def test_encode_typed_data_errors_on_unused_field_in_EIP712Domain():
    message_with_extra_EIP712Domain_field = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "number", "type": "uint256"},
            ],
            "Person": [
                {"name": "name", "type": "string"},
            ],
            "OtherPerson": [
                {"name": "name", "type": "string"},
            ],
        },
        "primaryType": "Person",
        "domain": {
            "name": "Name",
        },
        "message": {
            "name": "Bob",
        },
    }

    with pytest.raises(expected_exception=KeyError, match="number"):
        encode_structured_data(message_with_extra_EIP712Domain_field)


def test_encode_typed_data_ignores_extra_info_in_domain():
    message_with_extra_info_in_domain = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
            ],
            "Person": [
                {"name": "name", "type": "string"},
            ],
            "OtherPerson": [
                {"name": "name", "type": "string"},
            ],
        },
        "primaryType": "Person",
        "domain": {
            "name": "Name",
            "number": 27,
        },
        "message": {
            "name": "Bob",
        },
    }

    message_without_extra_info_in_domain = deepcopy(message_with_extra_info_in_domain)
    message_without_extra_info_in_domain["domain"].pop("number")
    assert message_without_extra_info_in_domain["domain"].get("number") is None

    assert encode_structured_data(
        message_with_extra_info_in_domain
    ) == encode_structured_data(message_without_extra_info_in_domain)
