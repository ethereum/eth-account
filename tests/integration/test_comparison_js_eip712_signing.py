import json
import subprocess

import pytest

from eth_account import (
    Account,
)
from eth_account.messages import (
    encode_structured_data,
    encode_typed_data,
)

TEST_KEY = "756e69636f726e73756e69636f726e73756e69636f726e73756e69636f726e73"

with open("tests/eip712_messages/valid.json") as f:
    valid_messages = json.load(f)




@pytest.mark.compatibility
@pytest.mark.parametrize("message_title", valid_messages)
def test_js_eip712_message_signing_matches_eth_account_sign_typed_data(message_title):
    message = valid_messages[message_title]

    message_stringify = json.dumps(message)
    # get ethers signature
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

    # breakpoint()

    # get metamask signature
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
    
    
    fresh_account = Account.from_key(TEST_KEY)

    try:
        signable_1 = encode_structured_data(message)
        py_signed_1 = fresh_account.sign_message(signable_1)
        py_old_sig = py_signed_1.signature.hex()
    except Exception as e:
        print(e)
        py_old_sig = "web3py_old signing failed"

    fresh_account = Account.from_key(TEST_KEY)
    try:
        signable_2 = encode_typed_data(full_message=message)
        py_signed_2 = fresh_account.sign_message(signable_2)
        py_new_one_arg = py_signed_2.signature.hex()
    except Exception as e:
        print(e)
        py_new_one_arg = "web3py_new_one_arg signing failed"

    def convert_to_3_arg(message):
        domain_data = message["domain"]
        message_types = message["types"]
        message_types.pop("EIP712Domain")
        message_data = message["message"]
        return domain_data, message_types, message_data

    fresh_account = Account.from_key(TEST_KEY)
    try:
        signable_3 = encode_typed_data(*convert_to_3_arg(message))
        py_signed_3 = fresh_account.sign_message(signable_3)
        py_new_three_arg = py_signed_3.signature.hex()
    except Exception as e:
        print(e)
        py_new_three_arg = "web3py_new_three_arg signing failed"
        
    # if message_title == "valid_issue_201_with_array":
    #     breakpoint()

    assert py_new_one_arg == py_new_three_arg == ethers_sig == metamask_sig

    # if (
    #     py_old_sig
    #     == ethers_sig
    #     == metamask_sig
    #     == py_new_one_arg
    #     == py_new_three_arg
    # ):
    #     print(py_old_sig)
    #     print("all sigs match")
    # else:
    #     print("sigs do not match")
    #     print(f"web3py_old: {py_old_sig}")
    #     print(f"web3py_new_one_arg: {py_new_one_arg}")
    #     print(f"web3py_new_three_arg: {py_new_three_arg}")
    #     print(f"ethers: {ethers_sig}")
    #     print(f"metamask: {metamask_sig}")
