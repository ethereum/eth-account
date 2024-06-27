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
from eth_keys.datatypes import (
    PrivateKey,
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
)


class AccountLocalActions(ABC):
    @classmethod
    @abstractmethod
    def encrypt(
        self,
        private_key: Union[HexStr, bytes, int, PrivateKey],
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
        private_key: Union[HexStr, bytes, int, PrivateKey],
    ) -> SignedMessage:
        pass

    @combomethod
    @abstractmethod
    def sign_message(
        self,
        signable_message: SignableMessage,
        private_key: Union[bytes, HexStr, int, PrivateKey],
    ) -> SignedMessage:
        pass

    @combomethod
    @abstractmethod
    def sign_transaction(
        self,
        transaction_dict: Dict[str, Any],
        private_key: Union[HexStr, bytes, int, PrivateKey],
        blobs: Optional[Blobs] = None,
    ) -> SignedTransaction:
        pass
