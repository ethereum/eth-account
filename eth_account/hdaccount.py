from os import (
    urandom,
)
from os.path import (
    dirname,
    join as ojoin,
    realpath,
)

from eth_account.datastructures import (
    AttributeDict,
)
from eth_account.hdaccount.deterministic import (
    bip32_ckd,
    bip32_deserialize,
    bip32_master_key,
)
from eth_account.hdaccount.mnemonic import (
    entropy_to_words,
    mnemonic_to_seed,
)
from eth_account.signers.base import (
    BaseAccount,
)

default_wordlist = ojoin(dirname(realpath(__file__)),
                         'hdaccount/wordlist/bip39_english.txt')


class HDAccount(BaseAccount):
    '''
    This class manages BIP32 HD-Accounts for Ethereum
    '''

    def __init__(self, encoded_key: str = "", path=[]):
        '''
        Constructor for this class. Initializes an hd account generator and
        if possible the encoded key and the derivation path. If no arguments are
        specified, create a new account with createAccount(...) or initialize
        an account given a mnemonic and an optional password with initAccount(...)
        :param str encoded_key  : (OPTIONAL) BIP32 serialized key
        :param path             : (OPTIONAL) derivation path, this is good to have
                                  but not necessary. Only relevant if you specify
                                  the encoded_key parameter
        :type path              : list as [idx_0, ..., idx_n] or str as either
                                  "idx_0/.../idx_n" or "m/idx_0/.../idx_n"
        '''

        # Contains derivation path. The class will automatically fill this
        self._path = []

        if isinstance(path, list):
            if len(path) != 0:
                for elem in path:
                    # Throws ValueError if elements are no base10 numbers
                    self._path.append(int(elem))
        elif isinstance(path, str):
            self._path = self.decodePath()
        else:
            raise TypeError("path has to be a list or a string")

        # Contains either encoded private key (hardened derivation possible)
        # or public key

        if not isinstance(encoded_key, str):
            raise TypeError("Encoded Key has to be a string")

        # Before assigning the key, check if it has the correct format
        if len(encoded_key) != 0:
            try:
                bip32_deserialize(encoded_key)
            except Exception as e:
                raise ValueError("encoded_key malformed: Not in bip32 serialized format.\n"
                                 "Additional informations: %s" % e)

        self.__key = encoded_key

        # Initiates the account generator
        self.__accgen = self._accountGenerator()
        self.__accgen.send(None)

        # Magic number for hardened key derivation (see BIP32)
        self._const_hardened = 0x80000000

    def _accountGenerator(self, cid: int = 0):
        '''
        This is the account generator used to derive all desired
        children keys. It is ought to be used only internally.
        You can either send None to this generator, in which case it
        just increments the index and returns you the derived child object
        for that index or you can send an index. Use self.__accgen to interact
        with this generator.
        :param int cid: Child index, leave empty to continue with last index + 1
        '''

        # This variable will contain the object of the last derived child
        newacc = None
        curindex = cid

        while True:
            cid = yield newacc

            # cid will be type and value checked and. If it is greater zero,
            # the next child index will be cid. If cid is const_magic_hardened,
            # the current index will be incremented by the hardened child
            # derivation constant

            if cid is not None:
                if not isinstance(cid, int):
                    raise TypeError("Invalid child index type. Excepted int")

                # else
                if cid >= 0:
                    curindex = cid
                else:
                    # cid == -1 means that we increase the old index by the
                    # hardened constant
                    if cid != -1:
                        raise ValueError("Invalid child index %d" % cid)

                    # else
                    if curindex < self._const_hardened:
                        curindex += self._const_hardened

            # Derive child. Will throw an error if hardened derivation is choosen
            # and only a pubkey is present
            newpath = self._path.copy()
            newpath.append(curindex)
            newacc = HDAccount(bip32_ckd(self.key, curindex), newpath)
            # increment index and yield new HDAccount object
            curindex += 1

    def deriveChild(self, cid: int = None, hardened: bool = False) -> "HDAccount":
        '''
        This function generates a new account by using the
        __accountGenerator function. You can specify an index.
        Not specifying an index leads to the usage of the old index + 1
        :param int cid      : (OPTIONAL) contains child index. Leave empty to use
                              the previous index + 1
        :param bool hardened: (OPTIONAL) if set to true, 0x80000000 will be added
                              to cid which leads to hardened key derivation.
        :returns            : HDAccount object for the desired index
        :rtype HDAccount
        '''

        # catch invalid argument type error, otherwise it will break our generator
        if cid is not None and not isinstance(cid, int):
            raise TypeError("Excepted integer as index")

        if not isinstance(hardened, bool):
            raise TypeError("Excepted bool for hardened")

        if isinstance(cid, int) and hardened is True:
            if cid >= self._const_hardened:
                raise ValueError("child index 0x%x is already >= 0x80000000 "
                                 "(hardened), but hardened is set to True")

            cid += self._const_hardened

        if cid is not None and cid < 0:
            raise ValueError("Negative child index not allowed")

        if cid is None and hardened is True:
            cid = -1

        return self.__accgen.send(cid)

    def derivePath(self, path) -> "HDAccount":
        '''
        This function receives a derivation path and returns
        an HDAccount object for the given path
        :param path     : contains the derivation path, example: "m/12H/1" or [0x8000000C, 1]
        :type path      : str or list
        :returns        : HDAccount object for the desired path
        :rtype HDAccount
        '''
        pass

    def createAccount(self, password: str = "", ent_bytes: int = 32, wordlist: str = None) -> str:
        '''
        This function initiates an account from scratch
        After completing the initiation it returns the mnemonic code
        :param list password  : (OPTIONAL) additional password for mnemonic
        :param list ent_bytes : (OPTIONAL) amount of entropy bytes for generations of the
                                mnemonic code has to be in [16, 20, 24, 28, 32]
        :param str wordlist   : (OPTIONAL) path to wordlist including name of wordlist,
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
        :param str password : (OPTIONAL) the password required to successfully
                              derive the master keys from the mnemonic code
        '''

        if isinstance(mnemonic, str):
            seed = mnemonic_to_seed(mnemonic.encode("utf-8"), password.encode("utf-8"))
        elif isinstance(mnemonic, list):
            seed = mnemonic_to_seed(" ".join(mnemonic).encode("utf-8"), password.encode("utf-8"))
        else:
            raise TypeError("Mnemonic has to be formated as a list or a string")

        # Create seed from mnemonic and derive key (in bip32 serialization format)
        self.__key = bip32_master_key(seed)
        self._path = []

    def decodePath(self, path: str):
        '''
        Converts the default string representation of a path to the internal
        representation using a list.
        :param str path : the string representation of the derivation path
        :returns        : list containing the derivation path
        :rtype          : list
        '''

        if not isinstance(path, str):
            raise TypeError("Excepted path as string")

        pathlist = path.split("/")

        # Basic (incomplete) checks if the path fits the standard notation
        if not path[0].isdigit():
            if not path[0].lower() == 'm':
                raise ValueError("Excepted path in the form m/idx1/idx2/... or"
                                 " idx1/idx2/...")
        else:
            if len(pathlist) == 1:
                raise ValueError("Excepted path in the form m/idx1/idx2/... or"
                                 " idx1/idx2/...")

        pathlist = pathlist[1:] if pathlist[0].lower() == 'm' else pathlist
        return [int(elem) if not elem[-1].lower() == 'h' else
                int(elem[:-1]) + self._const_hardened for elem in pathlist]

    @property
    def path(self):
        '''
        Returns the derivation path as a string of the form m/idx1/idx2 if the
        current object contains a complete path or idx1/idx otherwise
        :returns: derivation path
        :rtype  : str
        '''
        converted_ints = [str(idx) if idx < self._const_hardened else
                          str(idx - self._const_hardened) + 'H' for idx in self._path]

        depth = 0

        # In which derivation level is this object?
        if self.__key != "":
            depth = bip32_deserialize(self.__key)[1]

        # Full path available, so we can start with "m/"
        if depth == len(self._path):
            return "m/" + "/".join(converted_ints)
        else:
            return "/".join(converted_ints)

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

    def __repr__(self):
        '''
        Representation of this object. Use the output in your code to get
        the same object
        '''

        return "eth_account.hdaccount.HDAccount(encoded_key={}, path={})"\
            .format(self.key, self._path)

    def __str__(self):
        '''
        Human readable string represenation of this object
        '''

        return "Encoded key: {}\nDerivation Path: {}"\
            .format(self.key, self.path)

    def __eq__(self, other):
        '''
        Equality test between two accounts.
        Two accounts are considered the same if they are exactly the same type,
        and can sign for the same address.
        '''
        return type(self) == type(other) and self.key == other.key and \
            self.path == other.path

    def __hash__(self):
        '''
        Unique hash for this object
        '''

        return hash((type(self), self.key, self._path))


# Example on how to use this class
if __name__ == "__main__":
    # TEST 1: Create empty HDAccount object
    hdacc = HDAccount()

    # Create account
    print("Creating new Account")
    pw = "supersecret"
    mnemonic = hdacc.createAccount(pw)
    print("Mnemonic code: {}\nPassword: {}\nKey: {}\n".format(mnemonic, pw, hdacc.key))

    # TEST 2: Init account
    print("Initializing new Account with the same mnemonic and password")
    hdacc2 = HDAccount()
    hdacc2.initAccount(mnemonic, pw)
    print("Key: ", hdacc2.key)

    # Check if the creation of the account and the initialization share the same result
    assert(hdacc.key == hdacc2.key)
    print("\n")

    # TEST 3: Derive children using an index
    # can we derived an hardened key?
    newacc = hdacc.deriveChild(hardened=True)
    print(newacc)
    # can we set hardened=True twice without the hardened const being added twice?
    newacc = hdacc.deriveChild(hardened=True)
    print(newacc)
    # no arguments possible? (includes testing auto increment)
    newacc2 = newacc.deriveChild()
    print(newacc2)
    newacc2 = newacc.deriveChild()
    print(newacc2)
    # setting index manually possible?
    newacc2 = newacc2.deriveChild(42)
    print(newacc2)

    # TEST 4: Print empty HDAccount
    print(HDAccount())

    print("\nSuccess!\n")
