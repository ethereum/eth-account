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


def merge_dicts(*dict_args):
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


valid_for_all = load_file("valid_for_all.json")
valid_py_and_ethers = load_file("valid_py_and_ethers.json")
valid_py_and_metamask = load_file("valid_py_and_metamask.json")
valid = merge_dicts(valid_for_all, valid_py_and_ethers, valid_py_and_metamask)
valid_py_and_ethers = load_file("valid_py_and_ethers.json")
invalid = load_file("invalid.json")
one_arg_invalid = load_file("one_arg_invalid.json")


def convert_to_3_arg(message):
    domain_data = message["domain"]
    message_types = message["types"]
    message_types.pop("EIP712Domain", None)
    message_data = message["message"]
    return domain_data, message_types, message_data


@pytest.mark.parametrize("test_cases", (valid, invalid, one_arg_invalid))
def test_there_are_no_duplicate_test_cases(test_cases):
    string_test_cases = [json.dumps(msg, sort_keys=True) for msg in test_cases.values()]
    assert len(string_test_cases) == len(set(string_test_cases))


@pytest.mark.parametrize("message", valid)
def test_valid_messages(message):
    assert encode_typed_data(full_message=valid[message]) == encode_typed_data(
        *convert_to_3_arg(valid[message])
    )


@pytest.mark.parametrize("message", valid_py_and_ethers)
def test_valid_py_and_ethers_messages(message):
    assert encode_typed_data(
        full_message=valid_py_and_ethers[message]
    ) == encode_typed_data(*convert_to_3_arg(valid_py_and_ethers[message]))


@pytest.mark.parametrize("message", invalid)
def test_invalid_messages(message):
    with pytest.raises(ValueError):
        encode_typed_data(full_message=invalid[message])

    with pytest.raises(ValueError):
        encode_typed_data(*convert_to_3_arg(invalid[message]))


@pytest.mark.parametrize("message", one_arg_invalid)
def test_messages_that_are_only_invalid_for_one_arg_encoding(message):
    with pytest.raises(ValidationError):
        encode_typed_data(full_message=one_arg_invalid[message])
    encode_typed_data(*convert_to_3_arg(one_arg_invalid[message]))
