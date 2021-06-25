from typing import (
    Any,
    Dict,
)

from cytoolz import (
    dissoc,
    identity,
    merge,
    partial,
    pipe,
)
from eth_rlp import (
    HashableRLP,
)
from eth_utils import (
    is_address,
    keccak,
)
from eth_utils.curried import (
    apply_formatter_to_array,
    apply_formatters_to_dict,
    apply_formatters_to_sequence,
    apply_one_of_formatters,
    hexstr_if_str,
    is_bytes,
    is_list_like,
    is_string,
    to_bytes,
    to_int,
)
from hexbytes import (
    HexBytes,
)
import rlp
from rlp.sedes import (
    BigEndianInt,
    Binary,
    CountableList,
    List,
    big_endian_int,
    binary,
)

from .validation import (
    TRANSACTION_FORMATTERS,
    TRANSACTION_VALID_VALUES,
    is_int_or_prefixed_hexstr,
)

# Define typed transaction common sedes.
# [[{20 bytes}, [{32 bytes}...]]...], where ... means “zero or more of the thing to the left”.
access_list_sede_type = CountableList(
    List([
        Binary.fixed_length(20, allow_empty=False),
        CountableList(BigEndianInt(32)),
    ]),
)


class TypedTransaction():
    """
    Represents a Typed Transaction as per EIP-2718.
    The currently supported Transaction Types are:
     * EIP-2930's AccessListTransaction
    """
    def __init__(self, transaction_type, transaction):
        """Should not be called directly. Use instead the 'from_dict' method."""
        self.transaction_type = transaction_type
        self.transaction = transaction

    @classmethod
    def from_dict(cls, dictionary):
        """Builds a TypedTransaction from a dictionary. Verifies the dictionary is well formed."""
        if not ('type' in dictionary and is_int_or_prefixed_hexstr(dictionary['type'])):
            raise ValueError("missing or incorrect transaction type")
        # Switch on the transaction type to choose the correct constructor.
        transaction_type = pipe(dictionary['type'], hexstr_if_str(to_int))
        if transaction_type == AccessListTransaction.transaction_type:
            transaction = AccessListTransaction
        else:
            raise TypeError("Unknown Transaction type: %s" % transaction_type)
        return cls(
            transaction_type=transaction_type,
            transaction=transaction.from_dict(dictionary),
        )

    @classmethod
    def from_bytes(cls, encoded_transaction):
        """Builds a TypedTransaction from a signed encoded transaction."""
        if not isinstance(encoded_transaction, HexBytes):
            raise TypeError("expected Hexbytes, got type: %s" % type(encoded_transaction))
        if not (len(encoded_transaction) > 0 and encoded_transaction[0] <= 0x7f):
            raise ValueError("unexpected input")
        if encoded_transaction[0] == AccessListTransaction.transaction_type:
            transaction_type = AccessListTransaction.transaction_type
            transaction = AccessListTransaction.from_bytes(encoded_transaction)
        else:
            # The only known transaction types should be explit if/elif branches.
            raise TypeError("typed transaction has unknown type: %s" % encoded_transaction[0])
        return cls(
            transaction_type=transaction_type,
            transaction=transaction,
        )

    def hash(self):
        """
        Hashes this TypedTransaction to prepare it for signing. As per the EIP-2718 specifications,
        the hashing format is dictated by the transaction type itself, and so we delegate the call.
        Note that the return type will be bytes.
        """
        return self.transaction.hash()

    def encode(self):
        """
        Encodes this TypedTransaction and returns it as bytes. The transaction format follows
        EIP-2718's typed transaction format (TransactionType || TransactionPayload).
        Note that we delegate to a transaction type's payload() method as the EIP-2718 does not
        prescribe a TransactionPayload format, leaving types free to implement their own encoding.
        """
        return bytes([self.transaction_type]) + self.transaction.payload()

    def as_dict(self):
        """Returns this transaction as a dictionary."""
        return self.transaction.as_dict()

    def vrs(self):
        """Returns (v, r, s) if they exist."""
        return self.transaction.vrs()


class AccessListTransaction():
    """
    Represents an access list transaction per EIP-2930.
    """

    # This is the first transaction to implement the EIP-2978 typed transaction.
    transaction_type = 1  # '0x01'

    unsigned_transaction_fields = (
        ('chainId', big_endian_int),
        ('nonce', big_endian_int),
        ('gasPrice', big_endian_int),
        ('gas', big_endian_int),
        ('to', Binary.fixed_length(20, allow_empty=True)),
        ('value', big_endian_int),
        ('data', binary),
        ('accessList', access_list_sede_type),
    )

    signature_fields = (
        ('v', big_endian_int),
        ('r', big_endian_int),
        ('s', big_endian_int),
    )

    transaction_field_defaults = {
        'type': b'0x1',
        'chainId': 0,
        'to': b'',
        'value': 0,
        'data': b'',
        'accessList': [],
    }

    _unsigned_transaction_serializer = type(
        "_unsigned_transaction_serializer", (HashableRLP, ), {
            "fields": unsigned_transaction_fields,
        },
    )

    _signed_transaction_serializer = type(
        "_signed_transaction_serializer", (HashableRLP, ), {
            "fields": unsigned_transaction_fields + signature_fields,
        },
    )

    def __init__(self, dictionary):
        self.dictionary = dictionary

    @classmethod
    def is_access_list(cls, val):
        """Returns true if 'val' is a valid access list."""
        if not is_list_like(val):
            return False
        for item in val:
            if not is_list_like(item):
                return False
            if len(item) != 2:
                return False
            address, storage_keys = item
            if not is_address(address):
                return False
            for storage_key in storage_keys:
                if not is_int_or_prefixed_hexstr(storage_key):
                    return False
        return True

    @classmethod
    def assert_valid_fields(cls, dictionary):
        transaction_valid_values = merge(TRANSACTION_VALID_VALUES, {
            'type': is_int_or_prefixed_hexstr,
            'accessList': cls.is_access_list,
        })

        if 'v' in dictionary and dictionary['v'] == 0:
            # This is insane logic that is required because the way we evaluate
            # correct types is in the `if not all()` branch below, and 0 obviously
            # maps to the int(0), which maps to False... This was not an issue in non-typed
            # transaction because v=0, couldn't exist with the chain offset.
            dictionary['v'] = '0x0'
        valid_fields = apply_formatters_to_dict(
            transaction_valid_values, dictionary,
        )  # type: Dict[str, Any]
        if not all(valid_fields.values()):
            invalid = {key: dictionary[key] for key, valid in valid_fields.items() if not valid}
            raise TypeError("Transaction had invalid fields: %r" % invalid)

    @classmethod
    def from_dict(cls, dictionary):
        """
        Builds an AccessListTransaction from a dictionary.
        Verifies that the dictionary is well formed.
        """
        # Validate fields.
        cls.assert_valid_fields(dictionary)
        transaction_formatters = merge(TRANSACTION_FORMATTERS, {
            'chainId': hexstr_if_str(to_int),
            'type': hexstr_if_str(to_int),
            'accessList': apply_formatter_to_array(
                apply_formatters_to_sequence([
                    apply_one_of_formatters((
                        (is_string, hexstr_if_str(to_bytes)),
                        (is_bytes, identity),
                    )),
                    apply_formatter_to_array(hexstr_if_str(to_int)),
                ]),
            )
        })

        sanitized_dictionary = pipe(
            dictionary,
            dict,
            partial(merge, cls.transaction_field_defaults),
            apply_formatters_to_dict(transaction_formatters),
        )

        # We have verified the type, we can safely remove it from the dictionary,
        # given that it is not to be included within the RLP payload.
        transaction_type = sanitized_dictionary.pop('type')
        if transaction_type != cls.transaction_type:
            raise ValueError(
                "expected transaction type %s, got %s" % (cls.transaction_type, transaction_type),
            )
        assert transaction_type == cls.transaction_type
        return cls(
            dictionary=sanitized_dictionary,
        )

    @classmethod
    def from_bytes(cls, encoded_transaction):
        """Builds an AccesslistTransaction from a signed encoded transaction."""
        if not isinstance(encoded_transaction, HexBytes):
            raise TypeError("expected Hexbytes, got type: %s" % type(encoded_transaction))
        if not (len(encoded_transaction) > 0 and encoded_transaction[0] == cls.transaction_type):
            raise ValueError("unexpected input")
        # Format is (0x01 || TransactionPayload)
        # We strip the prefix, and RLP unmarshal the payload into our signed transaction serializer.
        transaction_payload = encoded_transaction[1:]
        dictionary = cls._signed_transaction_serializer.from_bytes(transaction_payload).as_dict()
        dictionary['type'] = cls.transaction_type
        return cls.from_dict(dictionary)

    def as_dict(self):
        """Returns this transaction as a dictionary."""
        dictionary = self.dictionary.copy()
        dictionary['type'] = self.__class__.transaction_type
        return dictionary

    def hash(self):
        """
        Hashes this AccessListTransaction to prepare it for signing.
        As per the EIP-2930 specifications, the signature is a secp256k1 signature over
        keccak256(0x01 || rlp([chainId, nonce, gasPrice, gasLimit, to, value, data, accessList])).
        Here, we compute the keccak256(...) hash.
        """
        # Remove signature fields.
        transaction_without_signature_fields = dissoc(self.dictionary, 'v', 'r', 's')
        rlp_serializer = self.__class__._unsigned_transaction_serializer
        hash = pipe(
            rlp_serializer.from_dict(transaction_without_signature_fields),
            lambda val: rlp.encode(val),  # rlp([...])
            lambda val: bytes([self.__class__.transaction_type]) + val,  # (0x01 || rlp([...]))
            keccak,  # keccak256(0x01 || rlp([...]))
        )
        return hash

    def payload(self):
        """
        Returns this transaction's payload as bytes. Here, the TransactionPayload = rlp([chainId,
        nonce, gasPrice, gasLimit, to, value, data, accessList, signatureYParity, signatureR,
        signatureS])
        """
        if not all(k in self.dictionary for k in 'vrs'):
            raise ValueError("attempting to encode an unsigned transaction")
        return rlp.encode(self.__class__._signed_transaction_serializer.from_dict(self.dictionary))

    def vrs(self):
        """Returns (v, r, s) if they exist."""
        if not all(k in self.dictionary for k in 'vrs'):
            raise ValueError("attempting to encode an unsigned transaction")
        return (self.dictionary['v'], self.dictionary['r'], self.dictionary['s'])
