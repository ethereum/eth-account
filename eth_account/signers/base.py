from abc import (
    ABC,
    abstractmethod,
)


class BaseAccount(ABC):
    '''
    Abstract class that defines a collection of convenience methods
    to sign transactions and message hashes.
    '''

    @property
    @abstractmethod
    def address(self):
        '''
        The checksummed public address for this account.

        .. code-block:: python

            >>> my_account.address
            "0xF0109fC8DF283027b6285cc889F5aA624EaC1F55"

        '''
        pass

    @abstractmethod
    def signHash(self, message_hash):
        '''
        Sign the hash of a message, as in :meth:`~eth_account.account.Account.signHash`
        but without specifying the private key.

        :var bytes message_hash: 32 byte hash of the message to sign
        '''
        pass

    @abstractmethod
    def signTransaction(self, transaction_dict):
        '''
        Sign a transaction, as in :meth:`~eth_account.account.Account.signTransaction`
        but without specifying the private key.

        :var dict transaction_dict: transaction with all fields specified
        '''
        pass

    def __eq__(self, other):
        '''
        Equality test between two accounts.

        Two accounts are considered the same if they are exactly the same type,
        and can sign for the same address.
        '''
        return type(self) == type(other) and self.address == other.address

    def __hash__(self):
        return hash((type(self), self.address))
