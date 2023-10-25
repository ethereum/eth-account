import json
import subprocess

import pytest

from eth_account import (
    Account,
)
from eth_account.messages import (
    encode_typed_data,
)

TEST_KEY = "756e69636f726e73756e69636f726e73756e69636f726e73756e69636f726e73"
py_account = Account.from_key(TEST_KEY)

with open("tests/eip712_messages/valid_for_all.json") as f:
    valid_messages = json.load(f)


with open("tests/eip712_messages/valid_py_and_ethers.json") as f:
    valid_py_and_ethers = json.load(f)


with open("tests/eip712_messages/valid_py_and_metamask.json") as f:
    valid_py_and_metamask = json.load(f)


def convert_to_3_arg(message):
    domain_data = message["domain"]
    message_types = message["types"]
    message_types.pop("EIP712Domain", None)
    message_data = message["message"]
    return domain_data, message_types, message_data


@pytest.mark.compatibility
@pytest.mark.parametrize("message_title", valid_messages)
def test_messages_where_all_3_sigs_match(message_title):
    message = valid_messages[message_title]
    message_stringify = json.dumps(message)

    ethers_sig = subprocess.run(
        [
            "node",
            "tests/integration/js-integration-test-scripts/sign-eip712-with-ethers",
            message_stringify,
            TEST_KEY,
        ],
        capture_output=True,
    )
    ethers_sig = ethers_sig.stdout.decode("utf-8").strip()

    metamask_sig = subprocess.run(
        [
            "node",
            "tests/integration/js-integration-test-scripts/sign-eip712-with-metamask",
            message_stringify,
            TEST_KEY,
        ],
        capture_output=True,
    )
    metamask_sig = metamask_sig.stdout.decode("utf-8").strip()

    try:
        signable_1 = encode_typed_data(full_message=message)
        py_signed_1 = py_account.sign_message(signable_1)
        py_one_arg = py_signed_1.signature.hex()
    except Exception as e:
        print(e)
        py_one_arg = "py_one_arg signing failed"

    try:
        signable_3 = encode_typed_data(*convert_to_3_arg(message))
        py_signed_3 = py_account.sign_message(signable_3)
        py_three_arg = py_signed_3.signature.hex()
    except Exception as e:
        print(e)
        py_three_arg = "py_three_arg signing failed"

    assert py_one_arg == py_three_arg == ethers_sig == metamask_sig


@pytest.mark.compatibility
@pytest.mark.parametrize("message_title", valid_py_and_ethers)
def test_messages_where_eth_account_matches_ethers_but_not_metamask(message_title):
    message = valid_py_and_ethers[message_title]
    message_stringify = json.dumps(message)

    ethers_sig = subprocess.run(
        [
            "node",
            "tests/integration/js-integration-test-scripts/sign-eip712-with-ethers",
            message_stringify,
            TEST_KEY,
        ],
        capture_output=True,
    )
    ethers_sig = ethers_sig.stdout.decode("utf-8").strip()

    metamask_sig = subprocess.run(
        [
            "node",
            "tests/integration/js-integration-test-scripts/sign-eip712-with-metamask",
            message_stringify,
            TEST_KEY,
        ],
        capture_output=True,
    )
    metamask_sig = metamask_sig.stdout.decode("utf-8").strip()

    try:
        signable_1 = encode_typed_data(full_message=message)
        py_signed_1 = py_account.sign_message(signable_1)
        py_one_arg = py_signed_1.signature.hex()
    except Exception as e:
        print(e)
        py_one_arg = "py_one_arg signing failed"

    try:
        signable_3 = encode_typed_data(*convert_to_3_arg(message))
        py_signed_3 = py_account.sign_message(signable_3)
        py_three_arg = py_signed_3.signature.hex()
    except Exception as e:
        print(e)
        py_three_arg = "py_three_arg signing failed"

    assert py_one_arg == py_three_arg == ethers_sig
    assert py_one_arg != metamask_sig


@pytest.mark.compatibility
@pytest.mark.parametrize("message_title", valid_py_and_metamask)
def test_messages_where_eth_account_matches_metamask_but_not_ethers(message_title):
    message = valid_py_and_metamask[message_title]
    message_stringify = json.dumps(message)

    ethers_sig = subprocess.run(
        [
            "node",
            "tests/integration/js-integration-test-scripts/sign-eip712-with-ethers",
            message_stringify,
            TEST_KEY,
        ],
        capture_output=True,
    )
    ethers_sig = ethers_sig.stdout.decode("utf-8").strip()

    metamask_sig = subprocess.run(
        [
            "node",
            "tests/integration/js-integration-test-scripts/sign-eip712-with-metamask",
            message_stringify,
            TEST_KEY,
        ],
        capture_output=True,
    )
    metamask_sig = metamask_sig.stdout.decode("utf-8").strip()

    try:
        signable_1 = encode_typed_data(full_message=message)
        py_signed_1 = py_account.sign_message(signable_1)
        py_one_arg = py_signed_1.signature.hex()
    except Exception as e:
        print(e)
        py_one_arg = "py_one_arg signing failed"

    try:
        signable_3 = encode_typed_data(*convert_to_3_arg(message))
        py_signed_3 = py_account.sign_message(signable_3)
        py_three_arg = py_signed_3.signature.hex()
    except Exception as e:
        print(e)
        py_three_arg = "py_three_arg signing failed"

    assert py_one_arg == py_three_arg == metamask_sig
    assert py_one_arg != ethers_sig
