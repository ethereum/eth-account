import os
import hmac
import hashlib
import struct
import codecs
import ecdsa

from hashlib import sha256
from ecdsa.curves import SECP256k1
from ecdsa.ecdsa import int_to_string, string_to_int

MIN_ENTROPY_LEN = 128        # bits
BIP32_HARDEN    = 0x80000000 # choose from hardened set of child keys
CURVE_GEN       = ecdsa.ecdsa.generator_secp256k1
CURVE_ORDER     = CURVE_GEN.order()
EX_MAIN_PRIVATE = [ codecs.decode('0488ade4', 'hex') ] # Version strings for mainnet extended private keys
EX_MAIN_PUBLIC  = [ codecs.decode('0488b21e', 'hex'), codecs.decode('049d7cb2', 'hex') ] # Version strings for mainnet extended public keys

__base58_alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__base58_alphabet_bytes = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__base58_radix = len(__base58_alphabet)

def __string_to_int(data):
    "Convert string of bytes Python integer, MSB"
    val = 0
    for (i, c) in enumerate(data[::-1]):
        val += (256**i)*c
    return val

def check_encode(raw):
    "Encode raw bytes into Bitcoin base58 string with checksum"
    chk = sha256(sha256(raw).digest()).digest()[:4]
    return encode(raw+chk)

def encode(data):
    "Encode bytes into Bitcoin base58 string"
    enc = ''
    val = __string_to_int(data)
    while val >= __base58_radix:
        val, mod = divmod(val, __base58_radix)
        enc = __base58_alphabet[mod] + enc
    if val:
        enc = __base58_alphabet[val] + enc

    # Pad for leading zeroes
    n = len(data)-len(data.lstrip(b'\0'))
    return __base58_alphabet[0]*n + enc

class HDAccount(object):

    # Static initializers to create from entropy
    @staticmethod
    def fromEntropy(entropy):
        "Create a HDAccount using supplied entropy >= MIN_ENTROPY_LEN"
        if entropy == None:
            entropy = os.urandom(MIN_ENTROPY_LEN/8) # Python doesn't have os.random()
        if not len(entropy) >= MIN_ENTROPY_LEN/8:
            raise ValueError("Initial entropy %i must be at least %i bits" %
                                (len(entropy), MIN_ENTROPY_LEN))
        I = hmac.new(b"Bitcoin seed", entropy, hashlib.sha512).digest()
        Il, Ir = I[:32], I[32:]
        key = HDAccount(secret=Il, chain=Ir, depth=0, index=0, fpr=b'\0\0\0\0')
        return key

    # Normal class initializer
    def __init__(self, secret, chain, depth, index, fpr):
        """
        Create a public or private HDAccount using key material and chain code.
        secret   This is the source material to generate the keypair, either a
                 32-byte string representation of a private key, or the ECDSA
                 library object representing a public key.
        chain    This is a 32-byte string representation of the chain code
        depth    Child depth; parent increments its own by one when assigning this
        index    Child index
        fpr      Parent fingerprint
        """
        self.k = ecdsa.SigningKey.from_string(secret, curve=SECP256k1)
        self.K = self.k.get_verifying_key()
        self.C = chain
        self.depth = depth
        self.index = index
        self.parent_fpr = fpr

    # Public methods
    def ExtendedKey(self, private=True, encoded=True):
        "Return extended private or public key as string, optionally Base58 encoded"
        version = EX_MAIN_PRIVATE[0] if private else EX_MAIN_PUBLIC[0]
        depth = bytes(bytearray([self.depth]))
        fpr = self.parent_fpr
        child = struct.pack('>L', self.index)
        chain = self.C
        if private is False:
            data = self.PublicKey()
        else:
            data = b'\x00' + self.PrivateKey()
        raw = version+depth+fpr+child+chain+data
        if not encoded:
            return raw
        else:
            return check_encode(raw)

    def PublicKey(self):
        "Return compressed public key encoding"
        padx = (b'\0'*32 + int_to_string(self.K.pubkey.point.x()))[-32:]
        if self.K.pubkey.point.y() & 1:
            ck = b'\3'+padx
        else:
            ck = b'\2'+padx
        return ck

    def PrivateKey(self):
        "Return private key as string"
        return self.k.to_string()

    def Fingerprint(self):
        "Return key fingerprint as string"
        cK = self.PublicKey()
        return hashlib.new('ripemd160', sha256(cK).digest()).digest()[:4]

    def ChildKey(self, i, harden=False):
        """
        Create a child key of index 'i'.
        If the most significant bit of 'i' is set, then select from the
        hardened key set, otherwise, select a regular child key.
        Returns a BIP32Key constructed with the child key parameters,
        or None if i index would result in an invalid key.
        """
        if (harden):
            i = i + BIP32_HARDEN

        # Index as bytes, BE
        i_str = struct.pack(">L", i)

        # Data to HMAC
        if i & BIP32_HARDEN:
            data = b'\0' + self.k.to_string() + i_str
        else:
            data = self.PublicKey() + i_str
        # Get HMAC of data
        I = hmac.new(self.C, data, hashlib.sha512).digest()
        Il, Ir = I[:32], I[32:]

        # Construct new key material from Il and current private key
        Il_int = string_to_int(Il)
        if Il_int > CURVE_ORDER:
            return None
        pvt_int = string_to_int(self.k.to_string())
        k_int = (Il_int + pvt_int) % CURVE_ORDER
        if (k_int == 0):
            return None
        secret = (b'\0'*32 + int_to_string(k_int))[-32:]
        
        # Construct and return a new HDAccount
        return HDAccount(secret=secret, chain=Ir, depth=self.depth+1, index=i, fpr=self.Fingerprint())
