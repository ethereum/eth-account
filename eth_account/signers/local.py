from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from eth_keyfile.keyfile import (
    KDFType,
)
from eth_keys.datatypes import (
    PrivateKey,
)
from eth_typing import (
    ChecksumAddress,
    Hash32,
)

# from eth_account.account import (
#     Account,
# )
from eth_account.datastructures import (
    SignedMessage,
    SignedTransaction,
)
from eth_account.messages import (
    SignableMessage,
)
from eth_account.signers.base import (
    BaseAccount,
)

# TODO can't import Account because circular
PlaceholderAccountType = Any


class LocalAccount(BaseAccount):
    r"""
    A collection of convenience methods to sign and encrypt, with an
    embedded private key.

    :var bytes key: the 32-byte private key data

    .. code-block:: python

        >>> my_local_account.address
        "0xF0109fC8DF283027b6285cc889F5aA624EaC1F55"
        >>> my_local_account.key
        b"\x01\x23..."

    You can also get the private key by casting the account to :class:`bytes`:

    .. code-block:: python

        >>> bytes(my_local_account)
        b"\\x01\\x23..."
    """

    def __init__(self, key: PrivateKey, account: PlaceholderAccountType):
        """
        Initialize a new account with the given private key.

        :param eth_keys.PrivateKey key: to prefill in private key execution
        :param ~eth_account.account.Account account: the key-unaware management API
        """
        self._publicapi: PlaceholderAccountType = account

        self._address: ChecksumAddress = key.public_key.to_checksum_address()

        key_raw: bytes = key.to_bytes()
        self._private_key = key_raw

        self._key_obj: PrivateKey = key

    @property
    def address(self) -> ChecksumAddress:
        return self._address

    @property
    def key(self) -> bytes:
        """
        Get the private key.
        """
        return self._private_key

    def encrypt(
        self,
        password: str,
        kdf: Optional[KDFType] = None,
        iterations: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate a string with the encrypted key.

        This uses the same structure as in
        :meth:`~eth_account.account.Account.encrypt`, but without a
        private key argument.
        """
        # type ignored need to refactor relation w Account to not have circular imports
        return self._publicapi.encrypt(  # type: ignore
            self.key, password, kdf=kdf, iterations=iterations
        )

    def unsafe_sign_hash(self, message_hash: Hash32) -> SignedMessage:
        # type ignored need to refactor relation w Account to not have circular imports
        return self._publicapi.unsafe_sign_hash(  # type: ignore
            message_hash,
            private_key=self.key,
        )

    def sign_message(self, signable_message: SignableMessage) -> SignedMessage:
        """
        Generate a string with the encrypted key.

        This uses the same structure as in
        :meth:`~eth_account.account.Account.sign_message`, but without a
        private key argument.
        """
        # type ignored need to refactor relation w Account to not have circular imports
        return self._publicapi.sign_message(  # type: ignore
            signable_message, private_key=self.key
        )

    def sign_transaction(
        self, transaction_dict: Dict[str, Any], blobs: Optional[List[bytes]] = None
    ) -> SignedTransaction:
        # type ignored need to refactor relation w Account to not have circular imports
        return self._publicapi.sign_transaction(  # type: ignore
            transaction_dict, self.key, blobs=blobs
        )

    def __bytes__(self) -> bytes:
        return self.key
