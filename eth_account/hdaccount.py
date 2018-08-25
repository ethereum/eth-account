from bitcoin import (
    deterministic,
    mnemonic,
)

from hexbytes import (
    HexBytes,
)

from eth_account.datastructures import (
    AttributeDict,
)

from eth_account.signers.base import (
    BaseAccount,
)


class HDAccount(BaseAccount):
    '''
    This class manages BIP32 HD-Accounts for Ethereum
    '''

    def __init__(self, privkey : str = "", pubkey : tuple = ("",""), chaindata : str = ""):
        ''' The object is getting initialized here. You can pass no parameters,
            in which case the object will be created containing no information.
            You can create an account later by calling initAccount(...) in this case.
            You can pass only a private key and chaindata, in which case the 
            public key will be automatically calculated. You can derive keypairs.
            You can pass only a public key and chaindata, in which case only
            public keys can be derived.
            Pass the arguments as hex strings.
        '''

        # bip32 magic number for derivation of hardened childs
        self.__hardened = 0x80000000

        if (privkey,pubkey,chaindata) == ("",("",""),""):
            # create uninitialized account
            self._privkey = self._chaindata = b""
            self._pubkey = (b"", b"")

        elif (privkey,chaindata) != ("",""):
            # initialize account with a private key and a chaincode
            # TODO
            # TODO derive public key

        elif (pubkey,chaindata) != ("",""):
            # initialize account only with a public key and a chaincode
            # TODO


        # Initiate account generator
        self._accgen = self._accountGenerator(0)
        next(self._accgen)

    def _accountGenerator(self, curindex : int = 0):
        ''' This is the account generator used to derive all desired
            children keys. It is ought to be used only internally.
            You can either send None to this generator, in which case it
            just increments the index and returns you the derived child object
            for that index or you can send an index.
            If no private key is specified but a public key is specified,
            the derived child will be derived using only the public key
        '''

        # This variable will contain the object of the last derived child
        newacc = None;

        while True:
            cid = yield newacc

            if (cid != None):
                if (type(cid) != type(1)):
                    raise TypeError("Invalid child index type. Excepted int")

                curindex = cid
                
            # TODO derive child into a new HDAccount object
            # z = HMAC-SHA512(chaincode, (maybe hardneed prefix) || compr. pubkey/privkey || index)
            # derivation index = z[:16]
            # new chaincode: z[16:]
            # private key: privkey += index
            # public key: publickey = pubkey ECC_ADD index ECC_MUL generator_point
            curindex += 1

    def deriveChild(self, cid : int = None) -> HDAccount:
        ''' This function generates a new account by using the
            __accountGenerator function. You can specify an index.
            Not specifying an index leads to the usage of the old index + 1
        '''
        # TODO implement this gateway function for __accountGenerator(...)
        # check if this object is initialized
        return self.__accgen.send(cid)

    def createAccount(self, password : str = "", ent_bits : int = 256) -> str:
        ''' This function initiates an account from scratch
            After completing the initiation it returns the mnemonic code
        '''
        # TODO random from ent pool -> add checksum -> create mnemonic ->
        # PBKDF2-HMAC-SHA512(mnemonic, pw) -> HMAC-SHA512(u"Bitcoin Seed", rootseed)
        # -> 32 Byte priv key | 32 Byte chaindata
        pass       

    @property
    def address(self) -> str:
        '''
        The checksummed public address for this account.
        .. code-block:: python
            >>> my_account.address
            "0xF0109fC8DF283027b6285cc889F5aA624EaC1F55"
        '''
        pass

    def signHash(self, message_hash : bytes) -> AttributeDict:
        '''
        Sign the hash of a message, as in :meth:`~eth_account.account.Account.signHash`
        but without specifying the private key.
        :var bytes message_hash: 32 byte hash of the message to sign
        '''
        pass

    def signTransaction(self, transaction_dict : Mapping) -> AttributeDict:
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
