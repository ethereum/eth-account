import pytest

from eth_utils import (
    ValidationError,
)

from eth_account.messages import (
    SignableMessage,
    encode_intended_validator,
)


@pytest.mark.parametrize(
    "primitive, hexstr, text, validator_address, expected_signable",
    (
        (b"", None, None, b"\xff" * 20, SignableMessage(b"\0", b"\xff" * 20, b"")),
        (
            b"",
            None,
            None,
            "0xFFfFfFffFFfffFFfFFfFFFFFffFFFffffFfFFFfF",
            SignableMessage(b"\0", b"\xff" * 20, b""),
        ),
        (None, "0x", None, b"\xff" * 20, SignableMessage(b"\0", b"\xff" * 20, b"")),
        (None, "", None, b"\xff" * 20, SignableMessage(b"\0", b"\xff" * 20, b"")),
        (None, None, "0x", b"\xff" * 20, SignableMessage(b"\0", b"\xff" * 20, b"0x")),
        (None, None, "", b"\xff" * 20, SignableMessage(b"\0", b"\xff" * 20, b"")),
    ),
)
def test_encode_intended_validator(
    primitive, hexstr, text, validator_address, expected_signable
):
    signable_message = encode_intended_validator(
        validator_address,
        primitive,
        hexstr=hexstr,
        text=text,
    )
    assert signable_message == expected_signable


@pytest.mark.parametrize(
    "invalid_address",
    (
        b"",
        "",
        None,
        # must be checksummed if hex-encoded
        "0xffffffffffffffffffffffffffffffffffffffff",
        b"\xff" * 19,
        b"\xff" * 21,
    ),
)
def test_encode_intended_validator_invalid_address(invalid_address):
    with pytest.raises(ValidationError):
        encode_intended_validator(invalid_address, b"")
