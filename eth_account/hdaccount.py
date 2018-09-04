from os import (
    urandom,
)
from os.path import (
    dirname,
    join as ojoin,
    realpath,
)

from eth_account.account import (
    Account,
)
from eth_account.datastructures import (
    AttributeDict,
)
from eth_account.hdaccount.deterministic import (
    PRIVATE,
    bip32_ckd,
    bip32_deserialize,
    bip32_master_key,
    bip32_privtopub,
)
from eth_account.hdaccount.mnemonic import (
    entropy_to_words,
    mnemonic_to_seed,
)
from eth_account.hdaccount.utils import (
    decompress,
)
from eth_account.signers.base import (
    BaseAccount,
)
from eth_keys import (
    KeyAPI,
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

        # Magic number for hardened key derivation (see BIP32)
        self._const_hardened = 0x80000000

        # Contains derivation path. The class will automatically fill this
        self._path = []

        if isinstance(path, list):
            if len(path) != 0:
                for elem in path:
                    # Throws ValueError if elements are no base10 numbers
                    self._path.append(int(elem))
        elif isinstance(path, str):
            self._path = self.decodePath(path)
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
            newacc = HDAccount(bip32_ckd(self.__key, curindex), newpath)
            # increment index and yield new HDAccount object
            curindex += 1

    def deriveChild(self, cid=None, hardened=False):
        '''
        This function generates a new account by using the
        __accountGenerator function. You can specify an index.
        Not specifying an index leads to the usage of the old index + 1
        :param int cid      : (OPTIONAL) contains child index. Leave empty to use
                              the previous index + 1
        :param bool hardened: (OPTIONAL) if set to true, 0x80000000 will be added
                              to cid which leads to hardened key derivation.
        :rtype HDAccount
        '''

        # catch invalid argument type error, otherwise it will break our generator
        if cid is not None and not isinstance(cid, int):
            raise TypeError("Excepted integer or None as index")

        if not isinstance(hardened, bool):
            raise TypeError("Excepted bool for hardened")

        if isinstance(cid, int) and hardened is True and not cid >= self._const_hardened:
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
        :param path     : contains the derivation path, either formated as
                          "(m/)idx_0/.../idx_n" or [idx_0, ..., idx_n]
        :type path      : str or list
        :returns        : HDAccount object for the desired path
        :rtype HDAccount
        '''

        if isinstance(path, list):
            enc_path = path
        elif isinstance(path, str):
            enc_path = self.decodePath(path)
        else:
            raise TypeError("path must be list or str in format (m/)/idx_1/.../idx_n")

        hdacc = self

        for idx in enc_path:
            hdacc = hdacc.deriveChild(idx)

        return hdacc

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

    def removePrivateKey(self):
        '''
        Removes a private key from this object and replaces it with a public key.
        From this moment on, only public keys can be derived from this object.
        '''
        if (self.__key == ""):
            return

        self.__key = bip32_privtopub(self.__key)

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
        Get the checksummed address of this hd account
        :returns: the checksummed public address for this account.
        :rtype  : str
        .. code-block:: python
            >>> my_account.address
            "0xF0109fC8DF283027b6285cc889F5aA624EaC1F55"
        '''

        rawtuple = bip32_deserialize(self.__key)

        key = rawtuple[-1]

        if rawtuple[0] in PRIVATE:
            # slice the last byte, since it is the WIF-Compressed information
            key = KeyAPI.PrivateKey(key[:-1]).public_key
        else:
            # remove 04 prefix for KeyAPI
            key = KeyAPI.PublicKey(decompress(key)[1:])

        return key.to_checksum_address()

    def signHash(self, message_hash):
        '''
        Sign the hash provided.

        .. WARNING:: *Never* sign a hash that you didn't generate,
            it can be an arbitrary transaction. For example, it might
            send all of your account's ether to an attacker.

        If you would like compatibility with
        :meth:`w3.eth.sign() <web3.eth.Eth.sign>`
        you can use :meth:`~eth_account.messages.defunct_hash_message`.

        Several other message standards are proposed, but none have a clear
        consensus. You'll need to manually comply with any of those message standards manually.

        :param message_hash: the 32-byte message hash to be signed
        :type message_hash: hex str, bytes or int
        :param private_key: the key to sign the message with
        :type private_key: hex str, bytes, int or :class:`eth_keys.datatypes.PrivateKey`
        :returns: Various details about the signature - most
          importantly the fields: v, r, and s
        :rtype: ~eth_account.datastructures.AttributeDict
        '''

        rawtuple = bip32_deserialize(self.__key)

        if rawtuple[0] in PRIVATE:
            # slice the last byte, since it is the WIF-Compressed information
            return Account.signHash(message_hash, rawtuple[5][:-1])

        if bip32_deserialize(self.__key)[0] not in PRIVATE:
            raise RuntimeError("Cannot sign, only the public key is available")

    def signTransaction(self, transaction_dict: dict) -> AttributeDict:
        '''
        Sign the hash provided.

        .. WARNING:: *Never* sign a hash that you didn't generate,
            it can be an arbitrary transaction. For example, it might
            send all of your account's ether to an attacker.

        If you would like compatibility with
        :meth:`w3.eth.sign() <web3.eth.Eth.sign>`
        you can use :meth:`~eth_account.messages.defunct_hash_message`.

        Several other message standards are proposed, but none have a clear
        consensus. You'll need to manually comply with any of those message standards manually.

        :param message_hash: the 32-byte message hash to be signed
        :type message_hash: hex str, bytes or int
        :param private_key: the key to sign the message with
        :type private_key: hex str, bytes, int or :class:`eth_keys.datatypes.PrivateKey`
        :returns: Various details about the signature - most
          importantly the fields: v, r, and s
        :rtype: ~eth_account.datastructures.AttributeDict
        '''

        rawtuple = bip32_deserialize(self.__key)

        if rawtuple[0] in PRIVATE:
            # slice the last byte, since it is the WIF-Compressed information
            return Account.signTransaction(transaction_dict, rawtuple[5][:-1])

        if bip32_deserialize(self.__key)[0] not in PRIVATE:
            raise RuntimeError("Cannot sign, only the public key is available")

    def __repr__(self):
        '''
        Representation of this object. Use the output in your code to get
        the same object
        :returns: string that shows how to get the same object
        :rtype  : str
        '''

        return "eth_account.hdaccount.HDAccount(encoded_key={}, path={})"\
            .format(self.key, self._path)

    def __str__(self):
        '''
        Human readable string represenation of this object
        :returns: string that represents the object in a human readable format
        :rtype  : str
        '''

        return "Encoded key: {}\nChecksummed address: {}\nDerivation Path: {}"\
            .format(self.key, self.address, self.path)

    def __eq__(self, other):
        '''
        Equality test between two accounts. 
        Two accounts are considered the same if they are exactly the same type,
        and can sign for the same address.
        :returns: boolean that indicates whether other is equal to this object
        :rtype  : bool
        '''
        return type(self) == type(other) and self.key == other.key and \
            self.path == other.path

    def __hash__(self):
        '''
        Unique hash for this object
        :returns: unique hash of this object
        :rtype  : int
        '''

        return hash((type(self), self.key, self._path))


# Example on how to use this class
if __name__ == "__main__":
    print("--- TEST 1: Create HDAccount ---\n\n")
    hdacc = HDAccount()

    # Create account
    print("Creating new Account")
    pw = "supersecret"
    mnemonic = hdacc.createAccount(pw)
    print("Mnemonic code: {}\nPassword: {}\nKey: {}\n".format(mnemonic, pw, hdacc.key))

    print("\n\n--- TEST2: Init account ---\n\n")
    hdacc2 = HDAccount()
    hdacc2.initAccount(mnemonic, pw)
    print("Key: ", hdacc2.key)

    # Check if the creation of the account and the initialization share the same result
    assert(hdacc.key == hdacc2.key)

    # can we derived an hardened key?
    print("\n\n--- TEST3: Derive children ---\n\n")
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

    print("\n\n--- TEST4: Remove private key (only public key derivation possible) ---\n\n")
    pubacc = HDAccount()
    pubacc.createAccount()
    # here we derive a child but self.__key is a xprv key
    pubacc.removePrivateKey()
    pubacc = pubacc.deriveChild()
    print(pubacc)
    # here we derive a child and self.__key is a xpub key
    pubacc = pubacc.deriveChild(42)
    print(pubacc)

    print("\n\n--- TEST 5: Derive path ---\n\n")
    path_from_test3_list = newacc2._path
    path_from_test3_str = newacc2.path
    # path as list
    newacc3 = HDAccount()
    newacc3.initAccount(mnemonic, pw)
    newacc3 = newacc3.derivePath(path_from_test3_list)
    print(newacc3)
    assert(newacc3 == newacc2)
    # path as string
    newacc3 = HDAccount()
    newacc3.initAccount(mnemonic, pw)
    newacc3 = newacc3.derivePath(path_from_test3_str)
    print(newacc3)
    assert(newacc3 == newacc2)

    print("\n\n--- TEST 6: Get address from xprv and xpub encoded keys ---\n\n")

    print(newacc3.address)
    print(pubacc.address)
    print("\nSuccess!\n")

    print("\n\n--- TEST 7: Sign message hash ---\n\n")
    randnum = urandom(32)
    msg = hex(int.from_bytes(randnum, "big"))
    print("signing key : %s" % newacc3.key)
    print("hash to sign: %s" % msg)
    print("Result:")
    print(newacc3.signHash(msg))

    print("\n\n--- TEST 8: Create and sign Transaction ---\n\n")
    testkey = "xprv9y8Gw5q3qFv42CiuohDV6L8gY9VHjs74dMKos2pVp74vyHFRiTHwPHFDAEgz" \
              "YDYDQYEh2yahi4Jga6qQn3q45yzvPcPibUaKNRrkTbsDHkK"
    testpath = "m/1H/1/42"
    testacc = HDAccount(testkey, testpath)
    transaction = {
        'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
        'value': 1000000000,
        'gas': 21000,
        'gasPrice': 2000000000,
        'nonce': 0,
        'chainId': 4
    }
    print(testacc)
    print("transaction to sign: ")
    print(transaction)
    print("Signed Transaction:")
    print(testacc.signTransaction(transaction))
