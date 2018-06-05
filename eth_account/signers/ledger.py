import struct
import itertools

import eth_utils
import rlp

import ledgerblue.comm

from hexbytes import HexBytes

from eth_account import (
    Account,
)

from eth_account.datastructures import (
    AttributeDict,
)

from eth_account.signers.base import (
    BaseAccount,
)

from eth_account.internal.transactions import (
    encode_transaction,
    serializable_unsigned_transaction_from_dict,
)

from eth_utils import (
    to_bytes,
    to_hex,
)

from eth_utils.curried import (
    keccak,
)


ETH_DERIVATION_PATH_PREFIX = "m/44'/60'/0'/"


class LedgerAccount(BaseAccount):
    '''
    Ledger Ethereum App Protocol Spec is located at:
    <https://github.com/LedgerHQ/blue-app-eth/blob/master/doc/ethapp.asc>

    References:
    - https://github.com/LedgerHQ/blue-app-eth/blob/master/getPublicKey.py
    - https://github.com/bargst/pyethoff/blob/master/tx_sign.py

    '''

    def __init__(self, account_id=0, address=None, path_prefix=ETH_DERIVATION_PATH_PREFIX):
        self.device = None
        self.path_prefix = path_prefix

        if eth_utils.is_address(address):
            self.account_id = self.get_account_id(address)
        else:
            self.account_id = account_id

    def _path_to_bytes(self, path):
        '''
        This function convert a bip32 string path to a bytes format used by the
        Ledger device. Path are of the form :

            m/ ? / ? / ? / ? .... with an arbitrary depth

        In most case, bip44 is used as a subset of bip32 with path of the form:

        m / purpose' / coin_type' / account' / change / address_index

        Apostrophe in the path indicates that bip32 hardened derivation is used.

        Ledger expect the following bytes input:
        1. Number of BIP 32 derivations to perform (max 10)
        2. First derivation index (big endian)
        3. Second derivation index (big endian)
        ...
        Nth. Last derivation index (big endian)

        References:
        - https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
        - https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki
        '''
        assert(path.startswith('m/'))

        elements = path.split('/')[1:]
        depth = len(elements)

        result = bytes([depth])  # Number of BIP 32 derivations to perform (max 10)

        for derivation_index in elements:
            # For each derivation index in the path check if it is hardened
            hardened = "'" in derivation_index
            index = int(derivation_index.strip("'"))

            if hardened:
                # See bip32 spec for hardened derivation spec
                index = 0x80000000 | index

            # Append index to result as a big-endian (>) unsigned int (I)
            result += struct.pack('>I', index)

        return result

    def _send_to_device(self, apdu):
        if self.device is None:
            self.device = ledgerblue.comm.getDongle(debug=True)

        reply = self.device.exchange(apdu, timeout=60)

        return reply

    @property
    def address(self):
        return self.get_address(self.account_id)

    def get_address(self, account_id):
        '''
        Query the ledger device for an ethereum address in HD wallet.
        Offset is the number in the HD wallet tree
        '''
        bip32_path = self._path_to_bytes(self.path_prefix + str(account_id))

        # https://github.com/LedgerHQ/blue-app-eth/blob/master/doc/ethapp.asc#get-eth-public-address
        apdu = bytes.fromhex('e0020000')
        apdu += bytes([len(bip32_path)])
        apdu += bip32_path

        result = self._send_to_device(apdu)

        # Parse result
        offset = 1 + result[0]
        address = result[offset + 1: offset + 1 + result[offset]]
        address = address.decode()  # Use decode() to convert from bytearray

        return eth_utils.to_normalized_address(address)

    def get_account_id(self, address, search_limit=20, search_account_id=0):
        '''
        Convert an address to the HD wallet tree account_id
        Start search at an account_id. This would allow to search deeper if required.
        Default search_limit at 20 take about 5s to reach.
        '''
        address = eth_utils.to_normalized_address(address)

        for account_id in itertools.count(start=search_account_id):
            if account_id > search_limit:
                raise ValueError(f'Address {address} not found' +
                                 f'(search_limit={search_limit}, ' +
                                 f'search_account_id={search_account_id})')
            if eth_utils.is_same_address(address, self.get_address(account_id)):
                return account_id

    def get_addresses(self, limit=5, page=0):
        '''
        List Ethereum HD wallet adrress of the ledger device
        '''
        return [self.get_address(account_id)
                for account_id in range(page * limit, (page + 1) * limit)]

    def signHash(self, message_hash):
        '''
        Not available with a Ledger
        '''
        raise NotImplementedError('signHash() is not available within ledger devices')

    def signTransaction(self, transaction_dict):
        '''
        Sign a transaction, as in :meth:`~eth_account.account.Account.signTransaction`
        but without specifying the private key.
        '''
        bip32_path = self._path_to_bytes(self.path_prefix + str(self.account_id))

        unsigned_transaction = serializable_unsigned_transaction_from_dict(transaction_dict)
        rlp_encoded_tx = rlp.encode(unsigned_transaction)

        # https://github.com/LedgerHQ/blue-app-eth/blob/master/doc/ethapp.asc#sign-eth-transaction
        apdu = bytes.fromhex('e0040000')
        apdu += bytes([len(bip32_path) + len(rlp_encoded_tx)])
        apdu += bip32_path
        apdu += rlp_encoded_tx

        # Sign with dongle
        result = self._send_to_device(apdu)

        # Retrieve VRS from sig
        v = result[0]
        r = int.from_bytes(result[1:1 + 32], 'big')
        s = int.from_bytes(result[1 + 32: 1 + 32 + 32], 'big')

        rlp_encoded = encode_transaction(unsigned_transaction, vrs=(v, r, s))
        transaction_hash = keccak(rlp_encoded)

        # Sanity check on the signed transaction
        expected_sender = self.address
        recover_sender = Account.recoverTransaction(rlp_encoded)
        assert eth_utils.is_same_address(expected_sender, recover_sender)

        return AttributeDict({
            'rawTransaction': HexBytes(rlp_encoded),
            'hash': HexBytes(transaction_hash),
            'v': v,
            'r': to_hex(r),
            's': to_hex(s),
        })

    def defunctSignMessage(self, primitive=None, hexstr=None, text=None):
        '''
        Sign a message with a hash as in :meth:`~eth_account.messages.defunct_hash_message`
        '''
        bip32_path = self._path_to_bytes(self.path_prefix + str(self.account_id))

        message_bytes = to_bytes(primitive, hexstr=hexstr, text=text)

        # https://github.com/LedgerHQ/blue-app-eth/blob/master/doc/ethapp.asc#sign-eth-transaction
        apdu = bytes.fromhex('e0080000')
        apdu += bytes([len(bip32_path) + len(message_bytes)])
        apdu += bip32_path
        apdu += message_bytes

        # Sign with dongle
        result = self._send_to_device(apdu) #TODO make it work ...

        # Retrieve VRS from sig
        v = result[0]
        r = int.from_bytes(result[1:1 + 32], 'big')
        s = int.from_bytes(result[1 + 32: 1 + 32 + 32], 'big')

        eth_signature_bytes = 'XXX' #TODO calculate using vrs

        return AttributeDict({
            'messageHash': msg_hash_bytes,
            'r': r,
            's': s,
            'v': v,
            'signature': HexBytes(eth_signature_bytes),
        })
