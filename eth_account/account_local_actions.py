from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Any,
)

from eth_keyfile.keyfile import (
    KDFType,
)
from eth_typing import (
    HexStr,
)
from eth_utils.curried import (
    combomethod,
)

from eth_account.datastructures import (
    SignedMessage,
    SignedTransaction,
)
from eth_account.messages import (
    SignableMessage,
)
from eth_account.typed_transactions.set_code_transaction import (
    SignedAuthorization,
)
from eth_account.types import (
    Blobs,
    PrivateKeyType,
    TransactionDictType,
)


class AccountLocalActions(ABC):
    @classmethod
    @abstractmethod
    def encrypt(
        self,
        private_key: PrivateKeyType,
        password: str,
        kdf: KDFType | None = None,
        iterations: int | None = None,
    ) -> dict[str, Any]:
        pass

    @combomethod
    @abstractmethod
    def unsafe_sign_hash(
        self,
        message_hash: HexStr | bytes | int,
        private_key: PrivateKeyType,
    ) -> SignedMessage:
        pass

    @combomethod
    @abstractmethod
    def sign_message(
        self,
        signable_message: SignableMessage,
        private_key: PrivateKeyType,
    ) -> SignedMessage:
        pass

    @combomethod
    @abstractmethod
    def sign_transaction(
        self,
        transaction_dict: TransactionDictType,
        private_key: PrivateKeyType,
        blobs: Blobs | None = None,
    ) -> SignedTransaction:
        pass

    @combomethod
    @abstractmethod
    def sign_typed_data(
        self,
        private_key: PrivateKeyType,
        domain_data: dict[str, Any] | None = None,
        message_types: dict[str, Any] | None = None,
        message_data: dict[str, Any] | None = None,
        full_message: dict[str, Any] | None = None,
    ) -> SignedMessage:
        pass

    @combomethod
    @abstractmethod
    def sign_authorization(
        self,
        private_key: PrivateKeyType,
        authorization: dict[str, Any],
    ) -> SignedAuthorization:
        pass
