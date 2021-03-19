import pytest

from eth_utils import (
    ValidationError,
)

from eth_account.messages import (
    EIP712Message,
    EIP712Type,
    SignableMessage,
    encode_intended_validator,
)


@pytest.mark.parametrize(
    'primitive, hexstr, text, validator_address, expected_signable',
    (
        (b'', None, None, b'\xff' * 20, SignableMessage(b'\0', b'\xff' * 20, b'')),
        (
            b'',
            None,
            None,
            '0xFFfFfFffFFfffFFfFFfFFFFFffFFFffffFfFFFfF',
            SignableMessage(b'\0', b'\xff' * 20, b''),
        ),
        (None, '0x', None, b'\xff' * 20, SignableMessage(b'\0', b'\xff' * 20, b'')),
        (None, '', None, b'\xff' * 20, SignableMessage(b'\0', b'\xff' * 20, b'')),
        (None, None, '0x', b'\xff' * 20, SignableMessage(b'\0', b'\xff' * 20, b'0x')),
        (None, None, '', b'\xff' * 20, SignableMessage(b'\0', b'\xff' * 20, b'')),
    )
)
def test_encode_intended_validator(primitive, hexstr, text, validator_address, expected_signable):
    signable_message = encode_intended_validator(
        validator_address,
        primitive,
        hexstr=hexstr,
        text=text,
    )
    assert signable_message == expected_signable


@pytest.mark.parametrize(
    'invalid_address',
    (
        b'',
        '',
        None,
        '0xffffffffffffffffffffffffffffffffffffffff',  # must be checksummed if hex-encoded
        b'\xff' * 19,
        b'\xff' * 21,
    ),
)
def test_encode_intended_validator_invalid_address(invalid_address):
    with pytest.raises(ValidationError):
        encode_intended_validator(invalid_address, b'')


class SubType(EIP712Type):
    inner: "uint256"


class ValidMsgDef(EIP712Message):
    _name_: "string" = "Name"

    value: "uint256"
    default_value: "address" = "0xFFfFfFffFFfffFFfFFfFFFFFffFFFffffFfFFFfF"
    sub: SubType


def test_multilevel_message():
    msg = ValidMsgDef(value=1, sub=SubType(inner=2))

    assert msg.version.hex() == "01"
    assert msg.header.hex() == "ae5d5ac778a755034e549ed137af5f5bf0aacf767321bb6127ec8a1e8c68714b"
    assert msg.body.hex() == "bbc572c6c3273deb6d95ffae1b79c35452b4996b81aa243b17eced03c0b01c54"
