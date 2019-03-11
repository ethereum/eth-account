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

from eth_account._utils.signing import (
    signature_wrapper,
)


def defunct_hash_message(
        primitive=None,
        *,
        hexstr=None,
        text=None,
        signature_version=b'E',
        version_specific_data=None):
    '''
    Convert the provided message into a message hash, to be signed.
    This provides the same prefix and hashing approach as
    :meth:`w3.eth.sign() <web3.eth.Eth.sign>`.
    Currently you can only specify the ``signature_version`` as following.
    version ``0x45`` (version ``E``): ``b'\\x19Ethereum Signed Message:\\n'``
    concatenated with the number of bytes in the message.
    .. note:: This is the defualt version followed, if the signature_version is not specified.
    version ``0x00`` (version ``0``): Sign data with intended validator (EIP 191).
    Here the version_specific_data would be a hexstr which is the 20 bytes account address
    of the intended validator.

    For version ``0x45`` (version ``E``), Awkwardly, the number of bytes in the message is
    encoded in decimal ascii. So if the message is 'abcde', then the length is encoded as the ascii
    character '5'. This is one of the reasons that this message format is not preferred.
    There is ambiguity when the message '00' is encoded, for example.
    Only use this method with version ``E`` if you must have compatibility with
    :meth:`w3.eth.sign() <web3.eth.Eth.sign>`.

    Supply exactly one of the three arguments:
    bytes, a hex string, or a unicode string.

    :param primitive: the binary message to be signed
    :type primitive: bytes or int
    :param str hexstr: the message encoded as hex
    :param str text: the message as a series of unicode characters (a normal Py3 str)
    :param bytes signature_version: a byte indicating which kind of prefix is to be added (EIP 191)
    :param version_specific_data: the data which is related to the prefix (EIP 191)
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
    recovery_hasher = compose(
        HexBytes,
        keccak,
        signature_wrapper(
            signature_version=signature_version,
            version_specific_data=version_specific_data,
        )
    )
    return recovery_hasher(message_bytes)
