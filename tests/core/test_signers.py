from eth_account import (
    Account,
)
from tests.eip712_messages import (
    ALL_VALID_EIP712_MESSAGES,
)


def test_sign_typed_data_signing_same_for_account_and_local_account():
    new_local_account = Account.create()
    for message in ALL_VALID_EIP712_MESSAGES.values():
        assert Account.sign_typed_data(
            new_local_account.key, full_message=message
        ) == new_local_account.sign_typed_data(full_message=message)
