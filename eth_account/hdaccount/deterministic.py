"""
Heirarchical Deterministic Wallet generator (HDWallet)

Partially implements the BIP-0032, BIP-0043, and BIP-0044 specifications:
BIP-0032: https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
BIP-0043: https://github.com/bitcoin/bips/blob/master/bip-0043.mediawiki
BIP-0044: https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki

Skips serialization and public key derivation as unnecssary for this library's purposes.

Notes
-----

* Integers are modulo the order of the curve (referred to as n).
* Addition (+) of two coordinate pair is defined as application of the EC group operation.
* Concatenation (||) is the operation of appending one byte sequence onto another.


Definitions
-----------

* point(p): returns the coordinate pair resulting from EC point multiplication
  (repeated application of the EC group operation) of the secp256k1 base point
  with the integer p.
* ser_32(i): serialize a 32-bit unsigned integer i as a 4-byte sequence,
  most significant byte first.
* ser_256(p): serializes the integer p as a 32-byte sequence, most significant byte first.
* ser_P(P): serializes the coordinate pair P = (x,y) as a byte sequence using SEC1's compressed
  form: (0x02 or 0x03) || ser_256(x), where the header byte depends on the parity of the
  omitted y coordinate.
* parse_256(p): interprets a 32-byte sequence as a 256-bit number, most significant byte first.

"""
# Additional notes:
# - This algorithm only implements private parent key → private child key CKD function,
#   as it is unnecessary to the HD key derivation functions used in this library to implement
#   the other functions (as Ethereum uses an Account-based system)
# - Unlike other libraries, this library does not use Bitcoin key serialization, because it is
#   not intended to be ultimately used for Bitcoin key derivations. This presents a simplified API.
from typing import (
    Tuple,
    Union,
)

from eth_utils import (
    to_int,
)

from ._utils import (
    SECP256K1_N,
    ec_point,
    hmac_sha512,
)


class Node(int):
    TAG = ""  # No tag
    OFFSET = 0x0  # No offset
    """
    Base node class
    """
    def __new__(cls, index):
        obj = int.__new__(cls, index + cls.OFFSET)
        obj.index = index
        return obj

    def __repr__(self):
        return f"{self.__class__.__name__}({self.index})"

    def __add__(self, other: int):
        return self.__class__(self.index + other)

    def serialize(self) -> bytes:
        assert 0 <= self < 2**32
        return self.to_bytes(4, byteorder="big")

    def encode(self) -> str:
        return str(self.index) + self.TAG

    @staticmethod
    def decode(node: str) -> Union["SoftNode", "HardNode"]:
        if len(node) < 1:
            raise ValueError("Cannot use empty string")
        if node[-1] in ("'", "H"):
            return HardNode(int(node[:-1]))
        else:
            return SoftNode(int(node))


class SoftNode(Node):
    """
    Soft node (unhardened), where value = index
    """
    TAG = ""  # No tag
    OFFSET = 0x0  # No offset


class HardNode(Node):
    """
    Hard node, where value = index + BIP32_HARDENED_CONSTANT
    """
    TAG = "H"  # "H" (or "'") means hard node (but use "H" for clarity)
    OFFSET = 0x80000000  # 2**31, BIP32 "Hardening constant"


def derive_child_key(
    parent_key: bytes,
    parent_chain_code: bytes,
    node: Node,
) -> Tuple[bytes, bytes]:
    """
    From BIP32:

    The function CKDpriv((k_par, c_par), i) → (k_i, c_i) computes a child extended
    private key from the parent extended private key:

    - Check whether i ≥ 2**31 (whether the child is a hardened key).
      - If so (hardened child):
        let I = HMAC-SHA512(Key = c_par, Data = 0x00 || ser_256(k_par) || ser_32(i)).
        (Note: The 0x00 pads the private key to make it 33 bytes long.)
      - If not (normal child):
        let I = HMAC-SHA512(Key = c_par, Data = ser_P(point(k_par)) || ser_32(i)).
    - Split I into two 32-byte sequences, I_L and I_R.
    - The returned child key k_i is parse_256(I_L) + k_par (mod n).
    - The returned chain code c_i is I_R.
    - In case parse_256(I_L) ≥ n or k_i = 0, the resulting key is invalid,
      and one should proceed with the next value for i.
      (Note: this has probability lower than 1 in 2**127.)
    """
    assert len(parent_chain_code) == 32
    if isinstance(node, HardNode):
        # NOTE Empty byte is added to align to SoftNode case
        assert len(parent_key) == 32  # Should be guaranteed here in return statment
        child = hmac_sha512(parent_chain_code, b"\x00" + parent_key + node.serialize())

    else:
        assert len(ec_point(parent_key)) == 33  # Should be guaranteed by Account class
        child = hmac_sha512(parent_chain_code, ec_point(parent_key) + node.serialize())

    assert len(child) == 64

    if to_int(child[:32]) >= SECP256K1_N:
        # Invalid key, compute using next node (< 2**-127 probability)
        return derive_child_key(parent_key, parent_chain_code, node + 1)

    child_key = (to_int(child[:32]) + to_int(parent_key)) % SECP256K1_N
    if child_key == 0:
        # Invalid key, compute using next node (< 2**-127 probability)
        return derive_child_key(parent_key, parent_chain_code, node + 1)
    return child_key.to_bytes(32, byteorder="big"), child[32:]


class HDPath:
    def __init__(self, path: str):
        """
        Constructor for this class. Initializes an hd account generator and
        if possible the encoded key and the derivation path. If no arguments are
        specified, create a new account with createAccount(...) or initialize
        an account given a mnemonic and an optional password with initAccount(...)
        :param path             : BIP32-compatible derivation path
        :type path              : str as "m/idx_0/.../idx_n" or "m/idx_0/.../idx_n"
                                  where idx_* is either an integer value (soft node)
                                  or an integer value followed by either the "'" char
                                  or the "H" char (hardened node)
        """
        nodes = path.split('/')
        if not nodes[0] == 'm':
            raise ValueError(f'Path is not valid: "{path}". Must start with "m"')
        decoded_path = []
        try:
            for node in nodes[1:]:  # We don't need the root node 'm'
                decoded_path.append(Node.decode(node))
        except ValueError as e:
            raise ValueError(f'Path is not valid: "{path}". Issue with node "{node}": {e}')
        self._path = decoded_path

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(path="{self.encode()}")'

    def encode(self) -> str:
        encoded_path = ['m']
        for node in self._path:
            encoded_path.append(node.encode())
        return '/'.join(encoded_path)

    def derive(self, seed: bytes) -> bytes:
        master_node = hmac_sha512(b"Bitcoin seed", seed)
        key = master_node[:32]
        chain_code = master_node[32:]
        for node in self._path:
            key, chain_code = derive_child_key(key, chain_code, node)
        return key
