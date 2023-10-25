import json
import os

from eth_utils import (
    ValidationError,
)
import pytest

from eth_account.messages import (
    encode_typed_data,
)


def load_file(file_name):
    with open(os.path.join("tests/eip712_messages", file_name), "r") as f:
        return json.load(f)


valid_for_all = load_file("valid_for_all.json")
valid_py_and_ethers = load_file("valid_py_and_ethers.json")
valid_py_and_metamask = load_file("valid_py_and_metamask.json")

VALID = {**valid_for_all, **valid_py_and_ethers, **valid_py_and_metamask}
INVALID = load_file("invalid.json")
ONE_ARG_INVALID = load_file("one_arg_invalid.json")


def convert_to_3_arg(message):
    domain_data = message["domain"]
    message_types = message["types"]
    message_types.pop("EIP712Domain", None)
    message_data = message["message"]
    return domain_data, message_types, message_data


@pytest.mark.parametrize("test_cases", (VALID, INVALID, ONE_ARG_INVALID))
def test_there_are_no_duplicate_test_cases(test_cases):
    string_test_cases = [json.dumps(msg, sort_keys=True) for msg in test_cases.values()]
    assert len(string_test_cases) == len(set(string_test_cases))


@pytest.mark.parametrize("message", VALID)
def test_valid_messages(message):
    assert encode_typed_data(full_message=VALID[message]) == encode_typed_data(
        *convert_to_3_arg(VALID[message])
    )


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
