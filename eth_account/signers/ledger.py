import itertools
import logging
import struct
import time

import eth_utils
from eth_utils import (
    to_bytes,
    to_hex,
    to_int,
)
from eth_utils.curried import (
    keccak,
)
from hexbytes import (
    HexBytes,
)
import rlp

from eth_account import (
    Account,
)
from eth_account.datastructures import (
    AttributeDict,
)
from eth_account.internal.transactions import (
    encode_transaction,
    serializable_unsigned_transaction_from_dict,
)
from eth_account.messages import (
    defunct_hash_message,
)
from eth_account.signers.base import (
    BaseAccount,
)
import hid

ETH_DERIVATION_PATH_PREFIX = "m/44'/60'/0'/"

CHANNEL_ID = 0x0101
TAG_APDU = 0x05
TAG_PING = 0x02

# Packet HEADER is defined at
# https://github.com/LedgerHQ/blue-app-eth/blob/master/doc/ethapp.asc#general-transport-description
#
# 1. Communication channel ID (big endian) value is always CHANNEL_ID
# 2. Command tag (TAG_APDU or TAG_PING)
# 3. Packet sequence index (big endian) starting at 0x00
#
PACKET_HEADER = struct.pack('>HBH', CHANNEL_ID, TAG_APDU, 0x00)
PACKET_SIZE = 64  # in bytes
PACKET_FREE = PACKET_SIZE - len(PACKET_HEADER)

RETURN_STATUS = {
    'OK': 0x9000,
    0x6700: 'Ethereum app not started on device',
    0x6d00: 'Ethereum app not started on device',
    0x6804: 'Ethereum app not ready on device',
    0x6985: 'User declined on device',
    0x6a80: 'Transaction data disabled on device'
}

# https://github.com/LedgerHQ/blue-app-eth/blob/master/src_genericwallet/main.c#L62
APDU_CLA = 0xE0
APDU_INS_GET_PUBLIC_KEY = 0x02
APDU_INS_SIGN = 0x04
APDU_INS_GET_APP_CONFIGURATION = 0x06
APDU_INS_SIGN_PERSONAL_MESSAGE = 0x08
APDU_P1_CONFIRM = 0x01
APDU_P1_NON_CONFIRM = 0x00
APDU_P2_NO_CHAINCODE = 0x00
APDU_P2_CHAINCODE = 0x01
APDU_P1_FIRST = 0x00
APDU_P1_MORE = 0x80

LEDGER_VENDOR_ID = 0x2c97
LEDGER_USAGE_PAGE_ID = 0xffa0


def wrap_apdu(command):
    '''
    Return a list of packet to be sent to the device
    '''
    packets = []

    # Prefix command with its length
    command = struct.pack('>H', len(command)) + command

    # Split command into at max PACKET_FREE sized chunks
    chunks = [command[i:i + PACKET_FREE] for i in range(0, len(command), PACKET_FREE)]

    # Create a packet for each command chunk
    for packet_id in range(len(chunks)):
        header = struct.pack('>HBH', CHANNEL_ID, TAG_APDU, packet_id)
        packet = header + chunks[packet_id]

        # Add padding to the packet to make it exactly PACKET_SIZE long
        packet.ljust(PACKET_SIZE, bytes([0x0]))

        packets.append(packet)

    return packets


def unwrap_apdu(packet):
    '''
    Given a packet from the device, extract and return relevant info
    '''
    if not packet:
        return (None, None, None, None, None)

    (channel, tag, packet_id, reply_size) = struct.unpack('>HBHH', packet[:7])

    if packet_id == 0:
        # reply_size is only valid in first reply
        return (channel, tag, packet_id, reply_size, packet[7:])
    else:
        return (channel, tag, packet_id, None, packet[5:])


class LedgerUsbException(Exception):
    pass


class LedgerUsbDevice:
    '''
    References:
    - https://github.com/LedgerHQ/blue-loader-python/blob/master/ledgerblue/comm.py#L56
    - https://github.com/ethereum/go-ethereum/blob/master/accounts/usbwallet/ledger.go
    '''

    logger = logging.getLogger('eth_account.signers.ledger.LedgerUsbDevices')

    def __init__(self):
        hidDevicePath = None
        for hidDevice in hid.enumerate(0, 0):
            if hidDevice['vendor_id'] == LEDGER_VENDOR_ID:
                if ('interface_number' in hidDevice and hidDevice['interface_number'] == 0) \
                   or ('usage_page' in hidDevice and
                        hidDevice['usage_page'] == LEDGER_USAGE_PAGE_ID):
                    hidDevicePath = hidDevice['path']
        if hidDevicePath is not None:
            dev = hid.device()
            dev.open_path(hidDevicePath)
            dev.set_nonblocking(True)
        else:
            raise LedgerUsbException('No Ledger usb device found')
        self.device = dev

    def exchange(self, apdu, timeout=20):
        self.logger.debug('Sending apdu to Ledger device: apdu={}'.format(to_hex(apdu)))

        # Construct the wrapped packets
        packets = wrap_apdu(apdu)

        # Send to device
        for packet in packets:
            self.device.write(packet)

        # Receive reply, size of reply is contained in first packet
        reply = []
        reply_min_size = 2
        reply_start = time.time()
        while True:
            packet = bytes(self.device.read(64))
            (channel, tag, index, size, data) = unwrap_apdu(packet)

            # Wait for a valid channel in replied packet
            if not channel:
                if reply_start + timeout < time.time():
                    message = 'Timeout waiting device response (timeout={}s)'
                    raise LedgerUsbException(message.format(timeout))
                time.sleep(0.01)
                continue

            # Check header validity of reply
            if channel != CHANNEL_ID or tag != TAG_APDU:
                raise LedgerUsbException('Invalid channel or tag, is "Browser' +
                                         ' support" disabled ?')

            # Size is not None only on first reply
            if size:
                reply_min_size = size

            reply += data

            # Check if we have received all the reply from device
            if len(reply) > reply_min_size:
                reply = bytes(reply[:reply_min_size])
                break

        # Status is stored at then end of the reply
        (status,) = struct.unpack('>H', reply[-2:])

        if status == RETURN_STATUS['OK']:
            message = 'Received apdu from Ledger device: apdu={}'
            self.logger.debug(message.format(to_hex(reply)))
            return reply[:-2]
        else:
            message = 'Invalid status in reply: {:#0x}'.format(status)
            if status in RETURN_STATUS:
                message += ' ({})'.format(RETURN_STATUS[status])
            raise LedgerUsbException(message)


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
            self.device = LedgerUsbDevice()

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
        apdu = struct.pack('>BBBB',
                           APDU_CLA, APDU_INS_GET_PUBLIC_KEY,
                           APDU_P1_NON_CONFIRM, APDU_P2_NO_CHAINCODE)
        apdu += struct.pack('>B', len(bip32_path))
        apdu += bip32_path

        result = self._send_to_device(apdu)

        # Parse result
        offset = 1 + result[0]
        address = result[offset + 1: offset + 1 + result[offset]]
        address = address.decode()  # Use decode() to convert from bytearray

        return eth_utils.to_checksum_address(address)

    def get_account_id(self, address, search_limit=20, search_account_id=0):
        '''
        Convert an address to the HD wallet tree account_id
        Start search at an account_id. This would allow to search deeper if required.
        Default search_limit at 20 take about 5s to reach.
        '''
        address = eth_utils.to_checksum_address(address)

        for account_id in itertools.count(start=search_account_id):
            if account_id > search_limit:
                raise ValueError('Address {} not found'.format(address) +
                                 '(search_limit={}, '.format(search_limit) +
                                 'account_id={})'.format(search_account_id))
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

        payload = bip32_path + rlp_encoded_tx

        # Split payload in chunks of 255 size
        chunks = [payload[i:i + 255] for i in range(0, len(payload), 255)]

        # https://github.com/LedgerHQ/blue-app-eth/blob/master/doc/ethapp.asc#sign-eth-transaction
        apdu_param1 = APDU_P1_FIRST
        for chunk in chunks:
            apdu = struct.pack('>BBBB',
                               APDU_CLA, APDU_INS_SIGN,
                               apdu_param1, APDU_P2_NO_CHAINCODE)
            apdu += struct.pack('>B', len(chunk))
            apdu += chunk

            # Send to dongle
            result = self._send_to_device(apdu)

            apdu_param1 = APDU_P1_MORE

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
            'r': to_int(r),
            's': to_int(s),
        })

    def defunctSignMessage(self, primitive=None, hexstr=None, text=None):
        '''
        Sign a message with a hash as in :meth:`~eth_account.messages.defunct_hash_message`

        Supported since firmware version 1.0.8
        '''
        bip32_path = self._path_to_bytes(self.path_prefix + str(self.account_id))

        message_bytes = to_bytes(primitive, hexstr=hexstr, text=text)

        # Prefix message with it's length as big-endian (>) unsigned int (I)
        message_with_prefix = struct.pack('>I', len(message_bytes)) + message_bytes

        payload = bip32_path + message_with_prefix

        # Split payload in chunks of 255 size
        chunks = [payload[i:i + 255] for i in range(0, len(payload), 255)]

        # https://github.com/LedgerHQ/blue-app-eth/blob/master/doc/ethapp.asc#sign-eth-personal-message
        apdu_param1 = APDU_P1_FIRST
        for chunk in chunks:
            apdu = struct.pack('>BBBB',
                               APDU_CLA, APDU_INS_SIGN_PERSONAL_MESSAGE,
                               apdu_param1, APDU_P2_NO_CHAINCODE)
            apdu += struct.pack('>B', len(chunk))
            apdu += chunk

            # Send to dongle
            result = self._send_to_device(apdu)

            apdu_param1 = APDU_P1_MORE

        # Retrieve VRS from sig
        v = result[0]
        r = int.from_bytes(result[1:1 + 32], 'big')
        s = int.from_bytes(result[1 + 32: 1 + 32 + 32], 'big')

        return AttributeDict({
            'messageHash': HexBytes(defunct_hash_message(message_bytes)),
            'signature': HexBytes(to_bytes(r) + to_bytes(s) + to_bytes(v)),
            'v': v,
            'r': to_int(r),
            's': to_int(s),
        })

    def get_version(self):
        '''
        Get version of the Ethereum application installed on the device.
        It also return if the application is configured to sign transaction
        with data.
        '''
        apdu = struct.pack('>BBBB',
                           APDU_CLA, APDU_INS_GET_APP_CONFIGURATION,
                           APDU_P1_NON_CONFIRM, APDU_P2_NO_CHAINCODE)

        result = self._send_to_device(apdu)

        # Parse result
        (data_sign, major_version, minor_version, patch_version) = struct.unpack('>?BBB', result)

        return (data_sign, major_version, minor_version, patch_version)
