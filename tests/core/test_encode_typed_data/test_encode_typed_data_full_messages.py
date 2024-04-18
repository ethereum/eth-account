import json
import pytest

from eth_utils import (
    ValidationError,
)

from eth_account.messages import (
    encode_typed_data,
)
from tests.eip712_messages import (
    ALL_VALID_EIP712_MESSAGES,
    INVALID,
    ONE_ARG_INVALID,
    convert_to_3_arg,
)


@pytest.mark.parametrize(
    "test_cases", (ALL_VALID_EIP712_MESSAGES, INVALID, ONE_ARG_INVALID)
)
def test_there_are_no_duplicate_test_cases(test_cases):
    string_test_cases = [json.dumps(msg, sort_keys=True) for msg in test_cases.values()]
    assert len(string_test_cases) == len(set(string_test_cases))


@pytest.mark.parametrize("message", ALL_VALID_EIP712_MESSAGES)
def test_valid_messages(message):
    assert encode_typed_data(
        full_message=ALL_VALID_EIP712_MESSAGES[message]
    ) == encode_typed_data(*convert_to_3_arg(ALL_VALID_EIP712_MESSAGES[message]))


@pytest.mark.parametrize("message", INVALID)
def test_invalid_messages(message):
    with pytest.raises(ValueError):
        encode_typed_data(full_message=INVALID[message])

    with pytest.raises(ValueError):
        encode_typed_data(*convert_to_3_arg(INVALID[message]))


@pytest.mark.parametrize("message", ONE_ARG_INVALID)
def test_messages_that_are_only_invalid_for_one_arg_encoding(message):
    with pytest.raises(ValidationError):
        encode_typed_data(full_message=ONE_ARG_INVALID[message])
    encode_typed_data(*convert_to_3_arg(ONE_ARG_INVALID[message]))
