from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Any,
    Dict,
    Optional,
    Union,
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
        kdf: Optional[KDFType] = None,
        iterations: Optional[int] = None,
    ) -> Dict[str, Any]:
        pass

    @combomethod
    @abstractmethod
    def unsafe_sign_hash(
        self,
        message_hash: Union[HexStr, bytes, int],
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
        blobs: Optional[Blobs] = None,
    ) -> SignedTransaction:
        pass
