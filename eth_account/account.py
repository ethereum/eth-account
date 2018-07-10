from collections import (
    Mapping,
)
import json
import os

from cytoolz import (
    dissoc,
)
from eth_keyfile import (
    create_keyfile_json,
    decode_keyfile_json,
)
from eth_keys import (
    KeyAPI,
    keys,
)
from eth_keys.exceptions import (
    ValidationError,
)
from eth_utils.curried import (
    combomethod,
    hexstr_if_str,
    is_dict,
    keccak,
    text_if_str,
    to_bytes,
    to_int,
)
from hexbytes import (
    HexBytes,
)

from eth_account.datastructures import (
    AttributeDict,
)
from eth_account.internal.signing import (
    hash_of_signed_transaction,
    sign_message_hash,
    sign_transaction_dict,
    to_standard_signature_bytes,
    to_standard_v,
)
from eth_account.internal.transactions import (
    Transaction,
    vrs_from,
)
from eth_account.signers.local import (
    LocalAccount,
)


class Account(object):
    '''
    This is the primary entry point for working with Ethereum private keys.

    It does **not** require a connection to an Ethereum node.
    '''
    _keys = keys

    @combomethod
    def create(self, extra_entropy=''):
        '''
        Creates a new private key, and returns it as a :class:`~eth_account.local.LocalAccount`.

        :param extra_entropy: Add extra randomness to whatever randomness your OS can provide
        :type extra_entropy: str or bytes or int
        :returns: an object with private key and convenience methods

        .. code-block:: python

            >>> from eth_account import Account
            >>> acct = Account.create('KEYSMASH FJAFJKLDSKF7JKFDJ 1530')
            >>> acct.address
            '0x5ce9454909639D2D17A3F753ce7d93fa0b9aB12E'
            >>> acct.privateKey
            b"\\xb2\\}\\xb3\\x1f\\xee\\xd9\\x12''\\xbf\\t9\\xdcv\\x9a\\x96VK-\\xe4\\xc4rm\\x03[6\\xec\\xf1\\xe5\\xb3d"

            # These methods are also available: signHash(), signTransaction(), encrypt()
            # They correspond to the same-named methods in Account.*
            # but without the private key argument
        '''
        extra_key_bytes = text_if_str(to_bytes, extra_entropy)
        key_bytes = keccak(os.urandom(32) + extra_key_bytes)
        return self.privateKeyToAccount(key_bytes)

    @staticmethod
    def decrypt(keyfile_json, password):
        '''
        Decrypts a private key that was encrypted using an Ethereum client or
        :meth:`~Account.encrypt`.

        :param keyfile_json: The encrypted key
        :type keyfile_json: dict or str
        :param str password: The password that was used to encrypt the key
        :returns: the raw private key
        :rtype: ~hexbytes.main.HexBytes

        .. code-block:: python

            >>> encrypted = {
             'address': '5ce9454909639d2d17a3f753ce7d93fa0b9ab12e',
             'crypto': {'cipher': 'aes-128-ctr',
              'cipherparams': {'iv': '78f214584844e0b241b433d7c3bb8d5f'},
              'ciphertext': 'd6dbb56e4f54ba6db2e8dc14df17cb7352fdce03681dd3f90ce4b6c1d5af2c4f',
              'kdf': 'pbkdf2',
              'kdfparams': {'c': 1000000,
               'dklen': 32,
               'prf': 'hmac-sha256',
               'salt': '45cf943b4de2c05c2c440ef96af914a2'},
              'mac': 'f5e1af09df5ded25c96fcf075ada313fb6f79735a914adc8cb02e8ddee7813c3'},
             'id': 'b812f3f9-78cc-462a-9e89-74418aa27cb0',
             'version': 3}

            >>> import getpass
            >>> Account.decrypt(encrypted, getpass.getpass())
            HexBytes('0xb25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364')

        '''
        if isinstance(keyfile_json, str):
            keyfile = json.loads(keyfile_json)
        elif is_dict(keyfile_json):
            keyfile = keyfile_json
        else:
            raise TypeError("The keyfile should be supplied as a JSON string, or a dictionary.")
        password_bytes = text_if_str(to_bytes, password)
        return HexBytes(decode_keyfile_json(keyfile, password_bytes))

    @staticmethod
    def encrypt(private_key, password):
        '''
        Creates a dictionary with an encrypted version of your private key.
        To import this keyfile into Ethereum clients like geth and parity:
        encode this dictionary with :func:`json.dumps` and save it to disk where your
        client keeps key files.

        :param private_key: The raw private key
        :type private_key: hex str, bytes, int or :class:`eth_keys.datatypes.PrivateKey`
        :param str password: The password which you will need to unlock the account in your client
        :returns: The data to use in your encrypted file
        :rtype: dict

        .. code-block:: python

            >>> import getpass
            >>> encrypted = Account.encrypt(
                0xb25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364,
                getpass.getpass()
            )

            {'address': '5ce9454909639d2d17a3f753ce7d93fa0b9ab12e',
             'crypto': {'cipher': 'aes-128-ctr',
              'cipherparams': {'iv': '78f214584844e0b241b433d7c3bb8d5f'},
              'ciphertext': 'd6dbb56e4f54ba6db2e8dc14df17cb7352fdce03681dd3f90ce4b6c1d5af2c4f',
              'kdf': 'pbkdf2',
              'kdfparams': {'c': 1000000,
               'dklen': 32,
               'prf': 'hmac-sha256',
               'salt': '45cf943b4de2c05c2c440ef96af914a2'},
              'mac': 'f5e1af09df5ded25c96fcf075ada313fb6f79735a914adc8cb02e8ddee7813c3'},
             'id': 'b812f3f9-78cc-462a-9e89-74418aa27cb0',
             'version': 3}

             >>> with open('my-keyfile', 'w') as f:
                 f.write(json.dumps(encrypted))
        '''
        if isinstance(private_key, keys.PrivateKey):
            key_bytes = private_key.to_bytes()
        else:
            key_bytes = HexBytes(private_key)

        password_bytes = text_if_str(to_bytes, password)
        assert len(key_bytes) == 32
        return create_keyfile_json(key_bytes, password_bytes)

    @combomethod
    def privateKeyToAccount(self, private_key):
        '''
        Returns a convenient object for working with the given private key.

        :param private_key: The raw private key
        :type private_key: hex str, bytes, int or :class:`eth_keys.datatypes.PrivateKey`
        :return: object with methods for signing and encrypting
        :rtype: LocalAccount

        .. code-block:: python

            >>> acct = Account.privateKeyToAccount(
              0xb25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364)
            >>> acct.address
            '0x5ce9454909639D2D17A3F753ce7d93fa0b9aB12E'
            >>> acct.privateKey
            b"\\xb2\\}\\xb3\\x1f\\xee\\xd9\\x12''\\xbf\\t9\\xdcv\\x9a\\x96VK-\\xe4\\xc4rm\\x03[6\\xec\\xf1\\xe5\\xb3d"

            # These methods are also available: signHash(), signTransaction(), encrypt()
            # They correspond to the same-named methods in Account.*
            # but without the private key argument
        '''
        key = self._parsePrivateKey(private_key)
        return LocalAccount(key, self)

    @combomethod
    def recoverHash(self, message_hash, vrs=None, signature=None):
        '''
        Get the address of the account that signed the message with the given hash.
        You must specify exactly one of: vrs or signature

        :param message_hash: the hash of the message that you want to verify
        :type message_hash: hex str or bytes or int
        :param vrs: the three pieces generated by an elliptic curve signature
        :type vrs: tuple(v, r, s), each element is hex str, bytes or int
        :param signature: signature bytes concatenated as r+s+v
        :type signature: hex str or bytes or int
        :returns: address of signer, hex-encoded & checksummed
        :rtype: str

        .. code-block:: python

            >>> msg = "I♥SF"
            >>> msghash = '0x1476abb745d423bf09273f1afd887d951181d25adc66c4834a70491911b7f750'
            >>> vrs = (
                  28,
                  '0xe6ca9bba58c88611fad66a6ce8f996908195593807c4b38bd528d2cff09d4eb3',
                  '0x3e5bfbbf4d3e39b1a2fd816a7680c19ebebaf3a141b239934ad43cb33fcec8ce')
            >>> Account.recoverHash(msghash, vrs=vrs)
            '0x5ce9454909639D2D17A3F753ce7d93fa0b9aB12E'

            # All of these recover calls are equivalent:

            # variations on msghash
            >>> msghash = b"\\x14v\\xab\\xb7E\\xd4#\\xbf\\t'?\\x1a\\xfd\\x88}\\x95\\x11\\x81\\xd2Z\\xdcf\\xc4\\x83JpI\\x19\\x11\\xb7\\xf7P"  # noqa: E501
            >>> Account.recoverHash(msghash, vrs=vrs)
            >>> msghash = 0x1476abb745d423bf09273f1afd887d951181d25adc66c4834a70491911b7f750
            >>> Account.recoverHash(msghash, vrs=vrs)

            # variations on vrs
            >>> vrs = (
                  '0x1c',
                  '0xe6ca9bba58c88611fad66a6ce8f996908195593807c4b38bd528d2cff09d4eb3',
                  '0x3e5bfbbf4d3e39b1a2fd816a7680c19ebebaf3a141b239934ad43cb33fcec8ce')
            >>> Account.recoverHash(msghash, vrs=vrs)
            >>> vrs = (
                  b'\\x1c',
                  b'\\xe6\\xca\\x9b\\xbaX\\xc8\\x86\\x11\\xfa\\xd6jl\\xe8\\xf9\\x96\\x90\\x81\\x95Y8\\x07\\xc4\\xb3\\x8b\\xd5(\\xd2\\xcf\\xf0\\x9dN\\xb3',  # noqa: E501
                  b'>[\\xfb\\xbfM>9\\xb1\\xa2\\xfd\\x81jv\\x80\\xc1\\x9e\\xbe\\xba\\xf3\\xa1A\\xb29\\x93J\\xd4<\\xb3?\\xce\\xc8\\xce')  # noqa: E501
            >>> Account.recoverHash(msghash, vrs=vrs)
            >>> vrs = (
                  0x1c,
                  0xe6ca9bba58c88611fad66a6ce8f996908195593807c4b38bd528d2cff09d4eb3,
                  0x3e5bfbbf4d3e39b1a2fd816a7680c19ebebaf3a141b239934ad43cb33fcec8ce)
            >>> Account.recoverHash(msghash, vrs=vrs)

            # variations on signature
            >>> signature = '0xe6ca9bba58c88611fad66a6ce8f996908195593807c4b38bd528d2cff09d4eb33e5bfbbf4d3e39b1a2fd816a7680c19ebebaf3a141b239934ad43cb33fcec8ce1c'  # noqa: E501
            >>> Account.recoverHash(msghash, signature=signature)
            >>> signature = b'\\xe6\\xca\\x9b\\xbaX\\xc8\\x86\\x11\\xfa\\xd6jl\\xe8\\xf9\\x96\\x90\\x81\\x95Y8\\x07\\xc4\\xb3\\x8b\\xd5(\\xd2\\xcf\\xf0\\x9dN\\xb3>[\\xfb\\xbfM>9\\xb1\\xa2\\xfd\\x81jv\\x80\\xc1\\x9e\\xbe\\xba\\xf3\\xa1A\\xb29\\x93J\\xd4<\\xb3?\\xce\\xc8\\xce\\x1c'  # noqa: E501
            >>> Account.recoverHash(msghash, signature=signature)
            >>> signature = 0xe6ca9bba58c88611fad66a6ce8f996908195593807c4b38bd528d2cff09d4eb33e5bfbbf4d3e39b1a2fd816a7680c19ebebaf3a141b239934ad43cb33fcec8ce1c  # noqa: E501
            >>> Account.recoverHash(msghash, signature=signature)
        '''
        hash_bytes = HexBytes(message_hash)
        if len(hash_bytes) != 32:
            raise ValueError("The message hash must be exactly 32-bytes")
        if vrs is not None:
            v, r, s = map(hexstr_if_str(to_int), vrs)
            v_standard = to_standard_v(v)
            signature_obj = self._keys.Signature(vrs=(v_standard, r, s))
        elif signature is not None:
            signature_bytes = HexBytes(signature)
            signature_bytes_standard = to_standard_signature_bytes(signature_bytes)
            signature_obj = self._keys.Signature(signature_bytes=signature_bytes_standard)
        else:
            raise TypeError("You must supply the vrs tuple or the signature bytes")
        pubkey = signature_obj.recover_public_key_from_msg_hash(hash_bytes)
        return pubkey.to_checksum_address()

    @combomethod
    def recoverTransaction(self, serialized_transaction):
        '''
        Get the address of the account that signed this transaction.

        :param serialized_transaction: the complete signed transaction
        :type serialized_transaction: hex str, bytes or int
        :returns: address of signer, hex-encoded & checksummed
        :rtype: str

        .. code-block:: python

            >>> raw_transaction = '0xf86a8086d55698372431831e848094f0109fc8df283027b6285cc889f5aa624eac1f55843b9aca008025a009ebb6ca057a0535d6186462bc0b465b561c94a295bdb0621fc19208ab149a9ca0440ffd775ce91a833ab410777204d5341a6f9fa91216a6f3ee2c051fea6a0428',  # noqa: E501
            >>> Account.recoverTransaction(raw_transaction)
            '0x2c7536E3605D9C16a7a3D7b1898e529396a65c23'
        '''
        txn_bytes = HexBytes(serialized_transaction)
        txn = Transaction.from_bytes(txn_bytes)
        msg_hash = hash_of_signed_transaction(txn)
        return self.recoverHash(msg_hash, vrs=vrs_from(txn))

    def setKeyBackend(self, backend):
        '''
        Change the backend used by the underlying eth-keys library.

        *(The default is fine for most users)*

        :param backend: any backend that works in
            `eth_keys.KeyApi(backend) <https://github.com/ethereum/eth-keys/#keyapibackendnone>`_

        '''
        self._keys = KeyAPI(backend)

    @combomethod
    def signHash(self, message_hash, private_key):
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

        .. code-block:: python

            >>> msg = "I♥SF"
            >>> from eth_account.messages import defunct_hash_message
            >>> msghash = defunct_hash_message(text=msg)
            HexBytes('0x1476abb745d423bf09273f1afd887d951181d25adc66c4834a70491911b7f750')
            >>> key = "0xb25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364"
            >>> Account.signHash(msghash, key)
            {'messageHash': HexBytes('0x1476abb745d423bf09273f1afd887d951181d25adc66c4834a70491911b7f750'),  # noqa: E501
             'r': 104389933075820307925104709181714897380569894203213074526835978196648170704563,
             's': 28205917190874851400050446352651915501321657673772411533993420917949420456142,
             'signature': HexBytes('0xe6ca9bba58c88611fad66a6ce8f996908195593807c4b38bd528d2cff09d4eb33e5bfbbf4d3e39b1a2fd816a7680c19ebebaf3a141b239934ad43cb33fcec8ce1c'),  # noqa: E501
             'v': 28}

            # these are equivalent:
            >>> Account.signHash(
                0x1476abb745d423bf09273f1afd887d951181d25adc66c4834a70491911b7f750,
                key
            )
            >>> Account.signHash(
                "0x1476abb745d423bf09273f1afd887d951181d25adc66c4834a70491911b7f750",
                key
            )
        '''
        msg_hash_bytes = HexBytes(message_hash)
        if len(msg_hash_bytes) != 32:
            raise ValueError("The message hash must be exactly 32-bytes")

        key = self._parsePrivateKey(private_key)

        (v, r, s, eth_signature_bytes) = sign_message_hash(key, msg_hash_bytes)
        return AttributeDict({
            'messageHash': msg_hash_bytes,
            'r': r,
            's': s,
            'v': v,
            'signature': HexBytes(eth_signature_bytes),
        })

    @combomethod
    def signTransaction(self, transaction_dict, private_key):
        '''
        Sign a transaction using a local private key. Produces signature details
        and the hex-encoded transaction suitable for broadcast using
        :meth:`w3.eth.sendRawTransaction() <web3.eth.Eth.sendRawTransaction>`.

        Create the transaction dict for a contract method with
        `my_contract.functions.my_function().buildTransaction()
        <http://web3py.readthedocs.io/en/latest/contracts.html#methods>`_

        :param dict transaction_dict: the transaction with keys:
          nonce, chainId, to, data, value, gas, and gasPrice.
        :param private_key: the private key to sign the data with
        :type private_key: hex str, bytes, int or :class:`eth_keys.datatypes.PrivateKey`
        :returns: Various details about the signature - most
          importantly the fields: v, r, and s
        :rtype: AttributeDict

        .. code-block:: python

            >>> transaction = {
                    # Note that the address must be in checksum format:
                    'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
                    'value': 1000000000,
                    'gas': 2000000,
                    'gasPrice': 234567897654321,
                    'nonce': 0,
                    'chainId': 1
                }
            >>> key = '0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318'
            >>> signed = Account.signTransaction(transaction, key)
            {'hash': HexBytes('0x6893a6ee8df79b0f5d64a180cd1ef35d030f3e296a5361cf04d02ce720d32ec5'),
             'r': 4487286261793418179817841024889747115779324305375823110249149479905075174044,
             'rawTransaction': HexBytes('0xf86a8086d55698372431831e848094f0109fc8df283027b6285cc889f5aa624eac1f55843b9aca008025a009ebb6ca057a0535d6186462bc0b465b561c94a295bdb0621fc19208ab149a9ca0440ffd775ce91a833ab410777204d5341a6f9fa91216a6f3ee2c051fea6a0428'),  # noqa: E501
             's': 30785525769477805655994251009256770582792548537338581640010273753578382951464,
             'v': 37}
            >>> w3.eth.sendRawTransaction(signed.rawTransaction)
        '''
        if not isinstance(transaction_dict, Mapping):
            raise TypeError("transaction_dict must be dict-like, got %r" % transaction_dict)

        account = self.privateKeyToAccount(private_key)

        # allow from field, *only* if it matches the private key
        if 'from' in transaction_dict:
            if transaction_dict['from'] == account.address:
                sanitized_transaction = dissoc(transaction_dict, 'from')
            else:
                raise TypeError("from field must match key's %s, but it was %s" % (
                    account.address,
                    transaction_dict['from'],
                ))
        else:
            sanitized_transaction = transaction_dict

        # sign transaction
        (
            v,
            r,
            s,
            rlp_encoded,
        ) = sign_transaction_dict(account._key_obj, sanitized_transaction)

        transaction_hash = keccak(rlp_encoded)

        return AttributeDict({
            'rawTransaction': HexBytes(rlp_encoded),
            'hash': HexBytes(transaction_hash),
            'r': r,
            's': s,
            'v': v,
        })

    @combomethod
    def _parsePrivateKey(self, key):
        '''
        Generate a :class:`eth_keys.datatypes.PrivateKey` from the provided key. If the
        key is already of type :class:`eth_keys.datatypes.PrivateKey`, return the key.

        :param key: the private key from which a :class:`eth_keys.datatypes.PrivateKey`
                    will be generated
        :type key: hex str, bytes, int or :class:`eth_keys.datatypes.PrivateKey`
        :returns: the provided key represented as a :class:`eth_keys.datatypes.PrivateKey`
        '''
        if isinstance(key, self._keys.PrivateKey):
            return key

        try:
            return self._keys.PrivateKey(HexBytes(key))
        except ValidationError as original_exception:
            raise ValueError(
                "The private key must be exactly 32 bytes long, instead of "
                "%d bytes." % len(key)
            ) from original_exception
