import json
import os


def load_eip712_json(file_name):
    with open(os.path.join("tests/eip712_messages", file_name)) as f:
        return json.load(f)


VALID_FOR_ALL = load_eip712_json("valid_for_all.json")
VALID_FOR_PY_AND_ETHERS = load_eip712_json("valid_py_and_ethers.json")
VALID_FOR_PY_AND_METAMASK = load_eip712_json("valid_py_and_metamask.json")
INVALID = load_eip712_json("invalid.json")
ONE_ARG_INVALID = load_eip712_json("one_arg_invalid.json")

ALL_VALID_EIP712_MESSAGES = {
    **VALID_FOR_ALL,
    **VALID_FOR_PY_AND_ETHERS,
    **VALID_FOR_PY_AND_METAMASK,
}


def convert_to_3_arg(message):
    domain_data = message["domain"]
    message_types = message["types"]
    message_types.pop("EIP712Domain", None)
    message_data = message["message"]
    return domain_data, message_types, message_data
