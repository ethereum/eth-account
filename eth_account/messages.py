from cytoolz import (
    compose,
)
from eth_utils import (
    keccak,
    to_bytes,
)
from hexbytes import (
    HexBytes,
)

from eth_account.internal.signing import (
    signature_wrapper,
)


def defunct_hash_message(primitive=None, hexstr=None, text=None):
    '''
    Convert the provided message into a message hash, to be signed.
    This provides the same prefix and hashing approach as
    :meth:`w3.eth.sign() <web3.eth.Eth.sign>`. That means that the
    message will automatically be prepended with text
    defined in EIP-191 as version 'E': ``b'\\x19Ethereum Signed Message:\\n'``
    concatenated with the number of bytes in the message.

    Awkwardly, the number of bytes in the message is encoded in decimal ascii. So
    if the message is 'abcde', then the length is encoded as the ascii
    character '5'. This is one of the reasons that this message format is not preferred.
    There is ambiguity when the message '00' is encoded, for example.
    Only use this method if you must have compatibility with
    :meth:`w3.eth.sign() <web3.eth.Eth.sign>`.

    Supply exactly one of the three arguments:
    bytes, a hex string, or a unicode string.

    :param primitive: the binary message to be signed
    :type primitive: bytes or int
    :param str hexstr: the message encoded as hex
    :param str text: the message as a series of unicode characters (a normal Py3 str)
    :returns: The hash of the message, after adding the prefix
    :rtype: ~hexbytes.main.HexBytes

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
    recovery_hasher = compose(HexBytes, keccak, signature_wrapper)
    return recovery_hasher(message_bytes)
