from typing import (
    NamedTuple,
)

from cytoolz import (
    compose,
)
from eth_typing import (
    Hash32,
)
from eth_utils.curried import (
    keccak,
    text_if_str,
    to_bytes,
    to_canonical_address,
    to_text,
    ValidationError,
)
from hexbytes import (
    HexBytes,
)

from eth_account._utils.signing import (
    signature_wrapper,
)
from eth_account._utils.structured_data.hashing import (
    hash_domain,
    hash_message as hash_eip712_message,
    load_and_validate_structured_message,
)
from eth_account._utils.validation import (
    is_valid_address,
)

text_to_bytes = text_if_str(to_bytes)


class SignableMessage(NamedTuple):
    """
    These are the components of an EIP-191_ signable message. Other message formats
    can be encoded into this format for easy signing. This data structure doesn't need to
    know about the original message format.

    .. _EIP-191: https://eips.ethereum.org/EIPS/eip-191
    """
    version: HexBytes  # must be length 1
    header: HexBytes  # aka "version specific data"
    body: HexBytes  # aka "data to sign"


def hash_eip191_message(signable_message: SignableMessage) -> Hash32:
    version = signable_message.version
    if len(version) != 1:
        raise ValidationError(
            "The supplied message version is {version!r}. "
            "The EIP-191 signable message standard only supports one-byte versions."
        )

    return keccak(
        b'\x19' +
        version +
        signable_message.header +
        signable_message.body
    )


def encode_intended_validator(
        validator_address,
        primitive: bytes = None,
        *,
        hexstr: str = None,
        text: str = None) -> SignableMessage:
    # TODO doc example
    """
    Supply exactly one of the three arguments:
    bytes as a primitive, a hex string, or a unicode string.

    :param primitive: the binary message to be signed
    :type primitive: bytes or int
    :param str hexstr: the message encoded as hex
    :param str text: the message as a series of unicode characters (a normal Py3 str)
    :returns: The EIP-191 encoded message, ready for signing

    """
    if not is_valid_address(validator_address):
        raise ValidationError(
            f"Cannot encode message with 'Validator Address': {validator_address}. "
            "It must be a checksum address, or an address converted to bytes."
        )
    message_bytes = to_bytes(primitive, hexstr=hexstr, text=text)
    return SignableMessage(
        b'\x00',  # version 0, as defined in EIP-191
        to_canonical_address(validator_address),
        message_bytes,
    )


# watch here for updates to signature format:
# https://github.com/ethereum/EIPs/blob/master/EIPS/eip-712.md
def encode_structured_data(
        primitive: bytes = None,
        *,
        hexstr: str = None,
        text: str = None) -> SignableMessage:
    """
    Supply exactly one of the three arguments:
    bytes as a primitive, a hex string, or a unicode string.

    :param primitive: the binary message to be signed
    :type primitive: bytes or int
    :param str hexstr: the message encoded as hex
    :param str text: the message as a series of unicode characters (a normal Py3 str)
    :returns: The EIP-191 encoded message, ready for signing

    """
    message_string = to_text(primitive, hexstr=hexstr, text=text)
    structured_data = load_and_validate_structured_message(message_string)
    return SignableMessage(
        b'\x01',
        hash_domain(structured_data),
        hash_eip712_message(structured_data),
    )


def encode_defunct(
        primitive: bytes = None,
        *,
        hexstr: str = None,
        text: str = None) -> SignableMessage:
    # TODO doc example
    '''
    Convert the provided message into a signable message.
    This provides the same prefix and hashing approach as
    :meth:`w3.eth.sign() <web3.eth.Eth.sign>`.

    EIP-191 defines this as "version ``E``".

    .. NOTE: This standard includes the number of bytes in the message as a part of the header.
        Awkwardly, the number of bytes in the message is encoded in decimal ascii.
        So if the message is 'abcde', then the length is encoded as the ascii
        character '5'. This is one of the reasons that this message format is not preferred.
        There is ambiguity when the message '00' is encoded, for example.

    Only use this method if you must have compatibility with
    :meth:`w3.eth.sign() <web3.eth.Eth.sign>`.

    Supply exactly one of the three arguments: bytes, a hex string, or a unicode string.

    :param primitive: the binary message to be signed
    :type primitive: bytes or int
    :param str hexstr: the message encoded as hex
    :param str text: the message as a series of unicode characters (a normal Py3 str)
    :returns: The EIP-191 encoded message, ready for signing

    .. code-block:: python

        >>> from eth_account.messages import defunct_hash_message

        >>> msg = "I♥SF"
        >>> defunct_hash_message(text=msg)
        HexBytes('0x1476abb745d423bf09273f1afd887d951181d25adc66c4834a70491911b7f750')

        # these four also produce the same hash:
        >>> defunct_hash_message(w3.toBytes(text=msg))
        HexBytes('0x1476abb745d423bf09273f1afd887d951181d25adc66c4834a70491911b7f750')

        >>> defunct_hash_message(bytes(msg, encoding='utf-8'))
        HexBytes('0x1476abb745d423bf09273f1afd887d951181d25adc66c4834a70491911b7f750')

        >>> Web3.toHex(text=msg)
        '0x49e299a55346'
        >>> defunct_hash_message(hexstr='0x49e299a55346')
        HexBytes('0x1476abb745d423bf09273f1afd887d951181d25adc66c4834a70491911b7f750')

        >>> defunct_hash_message(0x49e299a55346)
        HexBytes('0x1476abb745d423bf09273f1afd887d951181d25adc66c4834a70491911b7f750')
    '''
    message_bytes = to_bytes(primitive, hexstr=hexstr, text=text)
    msg_length = str(len(message_bytes)).encode('utf-8')

    # Encoding version E defined by EIP-191
    return SignableMessage(
        b'E',
        b'thereum Signed Message:\n' + msg_length,
        message_bytes,
    )


def defunct_hash_message(
        primitive: bytes = None,
        *,
        hexstr: str = None,
        text: str = None) -> SignableMessage:
    '''
    Convert the provided message into a message hash, to be signed.

    Intented for use with the deprecated Account.signHash(). This is for backwards compatibility
    only. All new implementations should use :meth:`encode_defunct` instead.

    :param primitive: the binary message to be signed
    :type primitive: bytes or int
    :param str hexstr: the message encoded as hex
    :param str text: the message as a series of unicode characters (a normal Py3 str)
    :returns: The hash of the message, after adding the prefix
    '''
    signable = encode_defunct(primitive, hexstr=hexstr, text=text)
    hashed = hash_eip191_message(signable)
    return HexBytes(hashed)
