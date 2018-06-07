from eth_account.signers.base import (
    BaseAccount,
)


class LocalAccount(BaseAccount):
    '''
    A collection of convenience methods to sign and encrypt, with an embedded private key.

    :var bytes privateKey: the 32-byte private key data

    .. code-block:: python

        >>> my_local_account.address
        "0xF0109fC8DF283027b6285cc889F5aA624EaC1F55"
        >>> my_local_account.privateKey
        b"\\x01\\x23..."

    You can also get the private key by casting the account to :class:`bytes`:

    .. code-block:: python

        >>> bytes(my_local_account)
        b"\\x01\\x23..."
    '''
    def __init__(self, key, account):
        '''
        :param eth_keys.PrivateKey key: to prefill in private key execution
        :param web3.account.Account account: the key-unaware management API
        '''
        self._publicapi = account

        self._address = key.public_key.to_checksum_address()

        key_raw = key.to_bytes()
        self._privateKey = key_raw

        self._key_obj = key

    @property
    def address(self):
        return self._address

    @property
    def privateKey(self):
        '''
        Get the private key.
        '''
        return self._privateKey

    def encrypt(self, password):
        '''
        Generate a string with the encrypted key, as in
        :meth:`~eth_account.account.Account.encrypt`, but without a private key argument.
        '''
        return self._publicapi.encrypt(self.privateKey, password)

    def signHash(self, message_hash):
        return self._publicapi.signHash(
            message_hash,
            private_key=self.privateKey,
        )

    def signTransaction(self, transaction_dict):
        return self._publicapi.signTransaction(transaction_dict, self.privateKey)

    def __bytes__(self):
        return self.privateKey
