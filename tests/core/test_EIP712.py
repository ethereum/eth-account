import json

from hexbytes import (
    HexBytes,
)
import pytest

from eth_utils import (
    keccak,
)

from eth_account import (
    Account,
)
from eth_account.messages import (
    defunct_hash_message,
)
from eth_account._utils.signing import (
    dependencies,
    encodeData,
    encodeType,
    hashStruct,
    typeHash,
)


@pytest.fixture
def structured_data_json_string():
    return '''{
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"}
            ],
            "Person": [
                {"name": "name", "type": "string"},
                {"name": "wallet", "type": "address"}
            ],
            "Mail": [
                {"name": "from", "type": "Person"},
                {"name": "to", "type": "Person"},
                {"name": "contents", "type": "string"}
            ]
        },
        "primaryType": "Mail",
        "domain": {
            "name": "Ether Mail",
            "version": "1",
            "chainId": 1,
            "verifyingContract": "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC"
        },
        "message": {
            "from": {
                "name": "Cow",
                "wallet": "0xCD2a3d9F938E13CD947Ec05AbC7FE734Df8DD826"
            },
            "to": {
                "name": "Bob",
                "wallet": "0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB"
            },
            "contents": "Hello, Bob!"
        }
    }'''


@pytest.fixture
def types(structured_data_json_string):
    return json.loads(structured_data_json_string)["types"]


@pytest.fixture
def domain_type(structured_data_json_string):
    return json.loads(structured_data_json_string)["types"]["EIP712Domain"]


@pytest.fixture
def message(structured_data_json_string):
    return json.loads(structured_data_json_string)["message"]


@pytest.fixture
def domain(structured_data_json_string):
    return json.loads(structured_data_json_string)["domain"]


@pytest.fixture(params=("text", "primitive", "hexstr"))
def signature_kwargs(request, structured_data_json_string):
    if request == "text":
        return {"text": structured_data_json_string}
    elif request == "primitive":
        return {"primitive": structured_data_json_string.encode()}
    else:
        return {"hexstr": structured_data_json_string.encode().hex()}


@pytest.mark.parametrize(
    'primary_type, expected',
    (
        ('Mail', ['Mail', 'Person']),
        ('Person', ['Person']),
    )
)
def test_dependencies(primary_type, types, expected):
    assert dependencies(primary_type, types) == expected


@pytest.mark.parametrize(
    'primary_type, expected',
    (
        ('Mail', 'Mail(Person from,Person to,string contents)Person(string name,address wallet)'),
        ('Person', 'Person(string name,address wallet)'),
    )
)
def test_encodeType(primary_type, types, expected):
    assert encodeType(primary_type, types) == expected


@pytest.mark.parametrize(
    'primary_type, expected_hex_value',
    (
        ('Mail', 'a0cedeb2dc280ba39b857546d74f5549c3a1d7bdc2dd96bf881f76108e23dac2'),
        ('Person', 'b9d8c78acf9b987311de6c7b45bb6a9c8e1bf361fa7fd3467a2163f994c79500'),
    )
)
def test_typeHash(primary_type, types, expected_hex_value):
    assert typeHash(primary_type, types).hex() == expected_hex_value


def test_encodeData(types, message):
    primary_type = "Mail"
    expected_hex_value = (
        "a0cedeb2dc280ba39b857546d74f5549c3a1d7bdc2dd96bf881f76108e23dac2fc71e5fa27ff56c350aa531b"
        "c129ebdf613b772b6604664f5d8dbe21b85eb0c8cd54f074a4af31b4411ff6a60c9719dbd559c221c8ac3492d9"
        "d872b041d703d1b5aadf3154a261abdd9086fc627b61efca26ae5702701d05cd2305f7c52a2fc8"
    )
    assert encodeData(primary_type, types, message).hex() == expected_hex_value


def test_hashStruct_main_message(structured_data_json_string):
    expected_hex_value = "c52c0ee5d84264471806290a3f2c4cecfc5490626bf912d01f240d7a274b371e"
    assert hashStruct(structured_data_json_string).hex() == expected_hex_value


def test_hashStruct_domain(structured_data_json_string):
    expected_hex_value = "f2cee375fa42b42143804025fc449deafd50cc031ca257e0b194a650a912090f"
    assert hashStruct(structured_data_json_string, for_domain=True).hex() == expected_hex_value


def test_hashed_structured_data(signature_kwargs):
    hashed_structured_msg = defunct_hash_message(
        **signature_kwargs,
        signature_version=b'\x01',
    )
    expected_hash_value_hex = "0xbe609aee343fb3c4b28e1df9e632fca64fcfaede20f02e86244efddf30957bd2"
    assert hashed_structured_msg.hex() == expected_hash_value_hex


def test_signature_verification(signature_kwargs):
    account = Account.create()
    hashed_structured_msg = defunct_hash_message(
        **signature_kwargs,
        signature_version=b'\x01',
    )
    signed = Account.signHash(hashed_structured_msg, account.privateKey)
    new_addr = Account.recoverHash(hashed_structured_msg, signature=signed.signature)
    assert new_addr == account.address


def test_signature_variables(signature_kwargs):
    # Check that the signature of typed message is the same as that
    # mentioned in the EIP. The link is as follows
    # https://github.com/ethereum/EIPs/blob/master/assets/eip-712/Example.js
    hashed_structured_msg = defunct_hash_message(
        **signature_kwargs,
        signature_version=b'\x01',
    )
    privateKey = keccak(text="cow")
    acc = Account.privateKeyToAccount(privateKey)
    assert HexBytes(acc.address) == HexBytes("0xcd2a3d9f938e13cd947ec05abc7fe734df8dd826")
    sig = Account.signHash(hashed_structured_msg, privateKey)
    assert sig.v == 28
    assert hex(sig.r) == "0x4355c47d63924e8a72e509b65029052eb6c299d53a04e167c5775fd466751c9d"
    assert hex(sig.s) == "0x7299936d304c153f6443dfa05f40ff007d72911b6f72307f996231605b91562"
