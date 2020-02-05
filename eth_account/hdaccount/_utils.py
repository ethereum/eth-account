import hashlib
import hmac

from eth_keys import (
    keys,
)
from hexbytes import (
    HexBytes,
)

SECP256K1_N = int("FFFFFFFF_FFFFFFFF_FFFFFFFF_FFFFFFFE_BAAEDCE6_AF48A03B_BFD25E8C_D0364141", 16)


def hmac_sha512(chain_code: bytes, data: bytes) -> bytes:
    """
    As specified by RFC4231 - https://tools.ietf.org/html/rfc4231
    """
    return hmac.new(chain_code, data, hashlib.sha512).digest()


def ec_point(pkey: bytes) -> bytes:
    """
    Compute `point(p)`, where `point` is ecdsa point multiplication

    Note: Result is ecdsa public key serialized to compressed form
    """
    return keys.PrivateKey(HexBytes(pkey)).public_key.to_compressed_bytes()
