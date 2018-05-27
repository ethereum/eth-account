class LocalAccount(object):
    '''
    A collection of convenience methods to sign and encrypt, with an embedded private key.

    :var str address: the checksummed public address for this account
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

        self.address = key.public_key.to_checksum_address()

        key_raw = key.to_bytes()
        self._privateKey = key_raw

        self._key_obj = key

    @property
    def privateKey(self):
        '''
        Get the private key.
        '''
        return self._privateKey

    def encrypt(self, password):
        '''
        Sign a message, as in :meth:`~eth_account.account.Account.encrypt`
        but without specifying the private key.
        '''
        return self._publicapi.encrypt(self.privateKey, password)

    def signHash(self, message_hash):
        '''
        Sign the hash of a message, as in :meth:`~eth_account.account.Account.signHash`
        but without specifying the private key.
        '''
        return self._publicapi.signHash(
            message_hash,
            private_key=self.privateKey,
        )

    def signTransaction(self, transaction_dict):
        '''
        Sign a transaction, as in :meth:`~eth_account.account.Account.signTransaction`
        but without specifying the private key.
        '''
        return self._publicapi.signTransaction(transaction_dict, self.privateKey)

    def __bytes__(self):
        return self.privateKey

    def __hash__(self):
        return hash(self.privateKey)

    def __eq__(self, other):
        return (isinstance(other, type(self))) and (self.privateKey == other.privateKey)
