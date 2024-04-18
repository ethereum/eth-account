import json
import pytest
import subprocess

from eth_account import (
    Account,
)
from eth_account.messages import (
    encode_typed_data,
)
from tests.eip712_messages import (
    VALID_FOR_ALL,
    VALID_FOR_PY_AND_ETHERS,
    VALID_FOR_PY_AND_METAMASK,
    convert_to_3_arg,
)

TEST_KEY = "756e69636f726e73756e69636f726e73756e69636f726e73756e69636f726e73"
py_account = Account.from_key(TEST_KEY)


def get_js_sig(message, library):
    message_stringify = json.dumps(message)
    sig = subprocess.run(
        [
            "node",
            f"tests/integration/js-scripts/sign-eip712-with-{library}",
            message_stringify,
            TEST_KEY,
        ],
        capture_output=True,
    )
    return sig.stdout.decode("utf-8").strip()


@pytest.mark.compatibility
@pytest.mark.parametrize("message_title", VALID_FOR_ALL)
def test_messages_where_all_3_sigs_match(message_title):
    message = VALID_FOR_ALL[message_title]

    ethers_sig = get_js_sig(message, "ethers")
    metamask_sig = get_js_sig(message, "metamask")

    try:
        signable_1 = encode_typed_data(full_message=message)
        py_signed_1 = py_account.sign_message(signable_1)
        py_one_arg = py_signed_1.signature.to_0x_hex()
    except Exception:
        py_one_arg = "py_one_arg signing failed"

    try:
        signable_3 = encode_typed_data(*convert_to_3_arg(message))
        py_signed_3 = py_account.sign_message(signable_3)
        py_three_arg = py_signed_3.signature.to_0x_hex()
    except Exception:
        py_three_arg = "py_three_arg signing failed"

    assert py_one_arg == py_three_arg == ethers_sig == metamask_sig


@pytest.mark.compatibility
@pytest.mark.parametrize("message_title", VALID_FOR_PY_AND_ETHERS)
def test_messages_where_eth_account_matches_ethers_but_not_metamask(message_title):
    message = VALID_FOR_PY_AND_ETHERS[message_title]

    ethers_sig = get_js_sig(message, "ethers")
    metamask_sig = get_js_sig(message, "metamask")

    try:
        signable_1 = encode_typed_data(full_message=message)
        py_signed_1 = py_account.sign_message(signable_1)
        py_one_arg = py_signed_1.signature.to_0x_hex()
    except Exception:
        py_one_arg = "py_one_arg signing failed"

    try:
        signable_3 = encode_typed_data(*convert_to_3_arg(message))
        py_signed_3 = py_account.sign_message(signable_3)
        py_three_arg = py_signed_3.signature.to_0x_hex()
    except Exception:
        py_three_arg = "py_three_arg signing failed"

    assert py_one_arg == py_three_arg == ethers_sig
    assert py_one_arg != metamask_sig


@pytest.mark.compatibility
@pytest.mark.parametrize("message_title", VALID_FOR_PY_AND_METAMASK)
def test_messages_where_eth_account_matches_metamask_but_not_ethers(message_title):
    message = VALID_FOR_PY_AND_METAMASK[message_title]

    ethers_sig = get_js_sig(message, "ethers")
    metamask_sig = get_js_sig(message, "metamask")

    try:
        signable_1 = encode_typed_data(full_message=message)
        py_signed_1 = py_account.sign_message(signable_1)
        py_one_arg = py_signed_1.signature.to_0x_hex()
    except Exception:
        py_one_arg = "py_one_arg signing failed"

    try:
        signable_3 = encode_typed_data(*convert_to_3_arg(message))
        py_signed_3 = py_account.sign_message(signable_3)
        py_three_arg = py_signed_3.signature.to_0x_hex()
    except Exception:
        py_three_arg = "py_three_arg signing failed"

    assert py_one_arg == py_three_arg == metamask_sig
    assert py_one_arg != ethers_sig
