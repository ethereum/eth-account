from os import (
    urandom,
)

from os.path import (
    join as ojoin,
    dirname,
    realpath,
)

from eth_account.datastructures import (
    AttributeDict,
)
from eth_account.signers.base import (
    BaseAccount,
)
from eth_account.hdaccount.deterministic import (
    bip32_master_key,
)
from eth_account.hdaccount.mnemonic import (
    entropy_to_words,
    mnemonic_to_seed,
)


default_wordlist = ojoin(dirname(realpath(__file__)),
                         'hdaccount/wordlist/bip39_english.txt')


class HDAccount(BaseAccount):
    '''
    This class manages BIP32 HD-Accounts for Ethereum
    '''

    def __init__(self, encoded_key=""):
        '''
        The object is getting initialized here. You can pass no parameters,
        in which case the object will be created containing no information.
        You can create an account later by calling createAccount(...) in this case.
        You can also initialize an account with a mnemonic code by using initAccount()
        You can pass only an encoded key, in which case the class is initialized
        by using the information contained within the encoded key.
        '''

        # Contains derivation path. The class will automatically fill this
        self._path = []

        # Contains either encoded private key (hardened derivation possible)
        # or public key
        self.__key = encoded_key

        # Initiates the account generator
        self.__accgen = self._accountGenerator()
        self.__accgen.send(None)

        # Magic number for hardened key derivation (see BIP32)
        self.__const_hardened = 0x80000000

    def _accountGenerator(self, curindex: int = 0):
        '''
        This is the account generator used to derive all desired
        children keys. It is ought to be used only internally.
        You can either send None to this generator, in which case it
        just increments the index and returns you the derived child object
        for that index or you can send an index.
        '''

        # This variable will contain the object of the last derived child
        newacc = None

        while True:
            cid = yield newacc

            if cid is not None:
                if not isinstance(cid, int):
                    raise TypeError("Invalid child index type. Excepted int")

                curindex = cid

            # TODO derive child into a new HDAccount object
            # z = HMAC-SHA512(chaincode, (maybe hardneed prefix) || compr. pubkey/privkey || index)
            # derivation index = z[:16]
            # new chaincode: z[16:]
            # private key: privkey += index
            # public key: publickey = pubkey ECC_ADD index ECC_MUL generator_point
            curindex += 1

    def deriveChild(self, cid: int = None) -> "HDAccount":
        '''
        This function generates a new account by using the
        __accountGenerator function. You can specify an index.
        Not specifying an index leads to the usage of the old index + 1
        :param int cid: (OPTIONAL) contains child index
        '''

        # catch invalid argument type error, otherwise it will break our generator
        if cid is not None or not isinstance(cid, int):
            raise TypeError("Excepted integer as index")

        # TODO implement this gateway function for __accountGenerator(...)
        # check if this object is initialized
        return self.__accgen.send(cid)

    def derivePath(self, path) -> "HDAccount":
        '''
        This function receives a derivation path and returns
        an HDAccount object for the given path
        :param path : contains the derivation path, example: "m/12H/1" or [0x8000000C, 1]
        :type path  : str or list
        :returns    : HDAccount for the desired path
        :rtype      : HDAccount
        '''
        pass

    def createAccount(self, password: str = "", ent_bytes: int = 32, wordlist: str = None) -> str:
        '''
        This function initiates an account from scratch
        After completing the initiation it returns the mnemonic code
        :param list password  : additional password for mnemonic
        :param list ent_bytes : amount of entropy bytes for generations of the
                                mnemonic code has to be in [16, 20, 24, 28, 32]
        :param str wordlist   : path to wordlist including name of wordlist,
                                defaults to english
        :returns              : mnemonic code
        :rtype str
        '''

        # generate mnemonic (uses english word book by default)
        # the function will perfom the value check for entropy bytes

        if wordlist is None:
            wordlist = default_wordlist

        with open(wordlist) as f_wl:
            wordlist_content = f_wl.readlines()

        mnemonic = entropy_to_words(urandom(ent_bytes), wordlist_content)
        self.initAccount(mnemonic, password)
        return " ".join(mnemonic)

    def initAccount(self, mnemonic, password: str = ""):
        '''
        This function initiates an account by using a mnemonic code
        and an optional password
        :param mnemonic     : the mnemonic code to derive the master keys from
        :type mnemonic      : str or list
        :param str password : the password required to successfully derive
                              the master keys from the mnemonic code
        '''

        if isinstance(mnemonic, str):
            seed = mnemonic_to_seed(mnemonic.encode("utf-8"), password.encode("utf-8"))
        elif isinstance(mnemonic, list):
            seed = mnemonic_to_seed(" ".join(mnemonic).encode("utf-8"), password.encode("utf-8"))
        else:
            raise TypeError("Mnemonic has to be formated as a list or a string")

        # create seed from mnemonic and derive key (in bip32 serialization format)
        self.__key = bip32_master_key(seed)

    @property
    def key(self):
        '''
        Returns the bip32 serialized key of this instance of HDAccount
        :returns: Bip32 serilaized key
        :rtype  : str
        '''

        return self.__key

    @property
    def address(self) -> str:
        '''
        The checksummed public address for this account.
        .. code-block:: python
            >>> my_account.address
            "0xF0109fC8DF283027b6285cc889F5aA624EaC1F55"
        '''
        pass

    def signHash(self, message_hash: bytes) -> AttributeDict:
        '''
        Sign the hash of a message, as in :meth:`~eth_account.account.Account.signHash`
        but without specifying the private key.
        :param bytes message_hash: 32 byte hash of the message to sign
        '''
        pass

    def signTransaction(self, transaction_dict: dict) -> AttributeDict:
        '''
        Sign a transaction, as in :meth:`~eth_account.account.Account.signTransaction`
        but without specifying the private key.
        :param dict transaction_dict: transaction with all fields specified
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


# Example on how to use this class
if __name__ == "__main__":
    # Create empty HDAccount object
    hdacc = HDAccount()

    # Create account
    print("Creating new Account")
    pw = "supersecret"
    mnemonic = hdacc.createAccount(pw)
    print("Mnemonic code: {}\nPassword: {}\nKey: {}\n".format(mnemonic, pw, hdacc.key))

    # Init account
    print("Initializing new Account with the same mnemonic and password")
    hdacc2 = HDAccount()
    hdacc2.initAccount(mnemonic, pw)
    print("Key: ", hdacc2.key)

    # Check if the creation of the account and the initialization share the same result
    assert(hdacc.key == hdacc2.key)
    print("Success!")
