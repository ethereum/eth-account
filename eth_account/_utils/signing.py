import json

from cytoolz import (
    curry,
    pipe,
)
from eth_utils import (
    keccak,
    to_bytes,
    to_int,
    to_text,
)
from eth_abi import (
    encode_abi,
)

from eth_account._utils.transactions import (
    ChainAwareUnsignedTransaction,
    UnsignedTransaction,
    encode_transaction,
    serializable_unsigned_transaction_from_dict,
    strip_signature,
)

CHAIN_ID_OFFSET = 35
V_OFFSET = 27

# signature versions
PERSONAL_SIGN_VERSION = b'E'  # Hex value 0x45
INTENDED_VALIDATOR_SIGN_VERSION = b'\x00'  # Hex value 0x00
STRUCTURED_DATA_SIGN_VERSION = b'\x01'  # Hex value 0x01


def sign_transaction_dict(eth_key, transaction_dict):
    # generate RLP-serializable transaction, with defaults filled
    unsigned_transaction = serializable_unsigned_transaction_from_dict(transaction_dict)

    transaction_hash = unsigned_transaction.hash()

    # detect chain
    if isinstance(unsigned_transaction, UnsignedTransaction):
        chain_id = None
    else:
        chain_id = unsigned_transaction.v

    # sign with private key
    (v, r, s) = sign_transaction_hash(eth_key, transaction_hash, chain_id)

    # serialize transaction with rlp
    encoded_transaction = encode_transaction(unsigned_transaction, vrs=(v, r, s))

    return (v, r, s, encoded_transaction)


#
# EIP712 Functionalities
#
def dependencies(primaryType, types, found=None):
    """
    Recursively get all the dependencies of the primaryType
    """
    # This is done to avoid the by-reference call of python
    found = found or []

    if primaryType in found:
        return found
    if primaryType not in types:
        return found

    found.append(primaryType)
    for field in types[primaryType]:
        for dep in dependencies(field["type"], types, found):
            if dep not in found:
                found.push(dep)

    return found


def dict_to_type_name_converter(field):
    """
    Given a dictionary ``field`` of type {'name': NAME, 'type': TYPE},
    this function converts it to ``TYPE NAME``
    """
    return field["type"] + " " + field["name"]


def encodeType(primaryType, types):
    # Getting the dependencies and sorting them alphabetically as per EIP712
    deps = dependencies(primaryType, types)
    deps_without_primary_type = list(filter(lambda x: x != primaryType, deps))
    sorted_deps = [primaryType] + sorted(deps_without_primary_type)

    result = ''.join(
        [
            dep + "(" + ','.join(map(dict_to_type_name_converter, types[dep])) + ")"
            for dep in sorted_deps
        ]
    )
    return result


def typeHash(primaryType, types):
    return keccak(text=encodeType(primaryType, types))


def encodeData(primaryType, types, data):
    encTypes = []
    encValues = []

    # Add typehash
    encTypes.append("bytes32")
    encValues.append(typeHash(primaryType, types))

    # Add field contents
    for field in types[primaryType]:
        value = data[field["name"]]
        if field["type"] == "string":
            # Special case where the values need to be keccak hashed before they are encoded
            encTypes.append("bytes32")
            hashed_value = keccak(text=value)
            encValues.append(hashed_value)
        elif field["type"] == "bytes":
            # Special case where the values need to be keccak hashed before they are encoded
            encTypes.append("bytes32")
            hashed_value = keccak(primitive=value)
            encValues.append(hashed_value)
        elif field["type"] in types:
            # This means that this type is a user defined type
            encTypes.append("bytes32")
            hashed_value = keccak(primitive=encodeData(field["type"], types, value))
            encValues.append(hashed_value)
        elif field["type"][-1] == "]":
            # TODO: Replace the above conditionality with Regex for identifying arrays declaration
            raise NotImplementedError("TODO: Arrays currently unimplemented in encodeData")
        else:
            encTypes.append(field["type"])
            encValues.append(value)

    return encode_abi(encTypes, encValues)


def hashStruct(structured_json_string_data, for_domain=False):
    """
    The structured_json_string_data is expected to have the ``types`` attribute and
    the ``primaryType``, ``message``, ``domain`` attribute.
    The ``for_domain`` variable is used to calculate the ``hashStruct`` as part of the
    ``domainSeparator`` calculation.
    """
    structured_data = json.loads(structured_json_string_data)
    types = structured_data["types"]
    if for_domain:
        primaryType = "EIP712Domain"
        data = structured_data["domain"]
    else:
        primaryType = structured_data["primaryType"]
        data = structured_data["message"]
    return keccak(encodeData(primaryType, types, data))


# watch here for updates to signature format: https://github.com/ethereum/EIPs/issues/191
@curry
def signature_wrapper(message, signature_version, version_specific_data):
    if not isinstance(message, bytes):
        raise TypeError("Message is of the type {}, expected bytes".format(type(message)))
    if not isinstance(signature_version, bytes):
        raise TypeError("Signature Version is of the type {}, expected bytes".format(
            type(signature_version))
        )

    if signature_version == PERSONAL_SIGN_VERSION:
        preamble = b'\x19Ethereum Signed Message:\n'
        size = str(len(message)).encode('utf-8')
        return preamble + size + message
    elif signature_version == INTENDED_VALIDATOR_SIGN_VERSION:
        wallet_address = to_bytes(hexstr=version_specific_data)
        if len(wallet_address) != 20:
            raise TypeError("Invalid Wallet Address: {}".format(version_specific_data))
        wrapped_message = b'\x19' + signature_version + wallet_address + message
        return wrapped_message
    elif signature_version == STRUCTURED_DATA_SIGN_VERSION:
        message_string = to_text(primitive=message)
        # Here the version_specific_data is the EIP712Domain JSON string (includes type also)
        domainSeparator = hashStruct(message_string, for_domain=True)
        wrapped_message = b'\x19' + signature_version + domainSeparator + hashStruct(message_string)
        return wrapped_message
    else:
        raise NotImplementedError(
            "Currently supported signature versions are: {0}, {1}, {2}. ".
            format(
                '0x' + INTENDED_VALIDATOR_SIGN_VERSION.hex(),
                '0x' + PERSONAL_SIGN_VERSION.hex(),
                '0x' + STRUCTURED_DATA_SIGN_VERSION.hex(),
            ) +
            "But received signature version {}".format('0x' + signature_version.hex())
        )


def hash_of_signed_transaction(txn_obj):
    '''
    Regenerate the hash of the signed transaction object.

    1. Infer the chain ID from the signature
    2. Strip out signature from transaction
    3. Annotate the transaction with that ID, if available
    4. Take the hash of the serialized, unsigned, chain-aware transaction

    Chain ID inference and annotation is according to EIP-155
    See details at https://github.com/ethereum/EIPs/blob/master/EIPS/eip-155.md

    :return: the hash of the provided transaction, to be signed
    '''
    (chain_id, _v) = extract_chain_id(txn_obj.v)
    unsigned_parts = strip_signature(txn_obj)
    if chain_id is None:
        signable_transaction = UnsignedTransaction(*unsigned_parts)
    else:
        extended_transaction = unsigned_parts + [chain_id, 0, 0]
        signable_transaction = ChainAwareUnsignedTransaction(*extended_transaction)
    return signable_transaction.hash()


def extract_chain_id(raw_v):
    '''
    Extracts chain ID, according to EIP-155
    @return (chain_id, v)
    '''
    above_id_offset = raw_v - CHAIN_ID_OFFSET
    if above_id_offset < 0:
        if raw_v in {0, 1}:
            return (None, raw_v + V_OFFSET)
        elif raw_v in {27, 28}:
            return (None, raw_v)
        else:
            raise ValueError("v %r is invalid, must be one of: 0, 1, 27, 28, 35+")
    else:
        (chain_id, v_bit) = divmod(above_id_offset, 2)
        return (chain_id, v_bit + V_OFFSET)


def to_standard_signature_bytes(ethereum_signature_bytes):
    rs = ethereum_signature_bytes[:-1]
    v = to_int(ethereum_signature_bytes[-1])
    standard_v = to_standard_v(v)
    return rs + to_bytes(standard_v)


def to_standard_v(enhanced_v):
    (_chain, chain_naive_v) = extract_chain_id(enhanced_v)
    v_standard = chain_naive_v - V_OFFSET
    assert v_standard in {0, 1}
    return v_standard


def to_eth_v(v_raw, chain_id=None):
    if chain_id is None:
        v = v_raw + V_OFFSET
    else:
        v = v_raw + CHAIN_ID_OFFSET + 2 * chain_id
    return v


def sign_transaction_hash(account, transaction_hash, chain_id):
    signature = account.sign_msg_hash(transaction_hash)
    (v_raw, r, s) = signature.vrs
    v = to_eth_v(v_raw, chain_id)
    return (v, r, s)


def _pad_to_eth_word(bytes_val):
    return bytes_val.rjust(32, b'\0')


def to_bytes32(val):
    return pipe(
        val,
        to_bytes,
        _pad_to_eth_word,
    )


def sign_message_hash(key, msg_hash):
    signature = key.sign_msg_hash(msg_hash)
    (v_raw, r, s) = signature.vrs
    v = to_eth_v(v_raw)
    eth_signature_bytes = to_bytes32(r) + to_bytes32(s) + to_bytes(v)
    return (v, r, s, eth_signature_bytes)
