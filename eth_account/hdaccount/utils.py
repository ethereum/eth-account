import binascii
import hashlib
import random
import re
from sys import (
    version_info,
)
import time

from eth_account.hdaccount import (
    pyspecials,
)

# import base64
# import hmac

'''
This library is composite from main.py in pybitcointools
https://github.com/vbuterin/pybitcointools/blob/aeb0a2bbb8bbfe421432d776c649650eaeb882a5/bitcoin/deterministic.py
'''


# Elliptic curve parameters (secp256k1)

P = 2**256 - 2**32 - 977
N = 115792089237316195423570985008687907852837564279074904382605163141518161494337
A = 0
B = 7
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
G = (Gx, Gy)


def change_curve(p, n, a, b, gx, gy):
    global P, N, A, B, Gx, Gy, G
    P, N, A, B, Gx, Gy = p, n, a, b, gx, gy
    G = (Gx, Gy)


def getG():
    return G

# Extended Euclidean Algorithm


def inv(a, n):
    if a == 0:
        return 0
    lm, hm = 1, 0
    low, high = a % n, n
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % n

# JSON access (for pybtctool convenience)


def access(obj, prop):
    if isinstance(obj, dict):
        if prop in obj:
            return obj[prop]
        elif '.' in prop:
            return obj[float(prop)]
        else:
            return obj[int(prop)]
    else:
        return obj[int(prop)]


def multiaccess(obj, prop):
    return [access(o, prop) for o in obj]


def slice(obj, start=0, end=2**200):
    return obj[int(start):int(end)]


def count(obj):
    return len(obj)


_sum = sum


def sum(obj):
    return _sum(obj)


def isinf(p):
    return p[0] == 0 and p[1] == 0


def to_jacobian(p):
    o = (p[0], p[1], 1)
    return o


def jacobian_double(p):
    if not p[1]:
        return (0, 0, 0)
    ysq = (p[1] ** 2) % P
    S = (4 * p[0] * ysq) % P
    M = (3 * p[0] ** 2 + A * p[2] ** 4) % P
    nx = (M**2 - 2 * S) % P
    ny = (M * (S - nx) - 8 * ysq ** 2) % P
    nz = (2 * p[1] * p[2]) % P
    return (nx, ny, nz)


def jacobian_add(p, q):
    if not p[1]:
        return q
    if not q[1]:
        return p
    U1 = (p[0] * q[2] ** 2) % P
    U2 = (q[0] * p[2] ** 2) % P
    S1 = (p[1] * q[2] ** 3) % P
    S2 = (q[1] * p[2] ** 3) % P
    if U1 == U2:
        if S1 != S2:
            return (0, 0, 1)
        return jacobian_double(p)
    H = U2 - U1
    R = S2 - S1
    H2 = (H * H) % P
    H3 = (H * H2) % P
    U1H2 = (U1 * H2) % P
    nx = (R ** 2 - H3 - 2 * U1H2) % P
    ny = (R * (U1H2 - nx) - S1 * H3) % P
    nz = (H * p[2] * q[2]) % P
    return (nx, ny, nz)


def from_jacobian(p):
    z = inv(p[2], P)
    return ((p[0] * z**2) % P, (p[1] * z**3) % P)


def jacobian_multiply(a, n):
    if a[1] == 0 or n == 0:
        return (0, 0, 1)

    if n == 1:
        return a

    if n < 0 or n >= N:
        return jacobian_multiply(a, n % N)

    if (n % 2) == 0:
        return jacobian_double(jacobian_multiply(a, n // 2))

    if (n % 2) == 1:
        return jacobian_add(jacobian_double(jacobian_multiply(a, n // 2)), a)


def fast_multiply(a, n):
    return from_jacobian(jacobian_multiply(to_jacobian(a), n))


def fast_add(a, b):
    return from_jacobian(jacobian_add(to_jacobian(a), to_jacobian(b)))

# Functions for handling pubkey and privkey formats


def get_pubkey_format(pub):
    if version_info.major == 2:
        two = '\x02'
        three = '\x03'
        four = '\x04'
    else:
        two = 2
        three = 3
        four = 4

    if isinstance(pub, (tuple, list)):
        return 'decimal'
    elif len(pub) == 65 and pub[0] == four:
        return 'bin'
    elif len(pub) == 130 and pub[0:2] == '04':
        return 'hex'
    elif len(pub) == 33 and pub[0] in [two, three]:
        return 'bin_compressed'
    elif len(pub) == 66 and pub[0:2] in ['02', '03']:
        return 'hex_compressed'
    elif len(pub) == 64:
        return 'bin_electrum'
    elif len(pub) == 128:
        return 'hex_electrum'
    else:
        raise Exception("Pubkey not in recognized format")


def encode_pubkey(pub, formt):
    if not isinstance(pub, (tuple, list)):
        pub = decode_pubkey(pub)

    if formt == 'decimal':
        return pub
    elif formt == 'bin':
        return b'\x04' + pyspecials.encode(pub[0], 256, 32) + pyspecials.encode(pub[1], 256, 32)
    elif formt == 'bin_compressed':
        return pyspecials.from_int_to_byte(2 + (pub[1] % 2)) + pyspecials.encode(pub[0], 256, 32)
    elif formt == 'hex':
        return '04' + pyspecials.encode(pub[0], 16, 64) + pyspecials.encode(pub[1], 16, 64)
    elif formt == 'hex_compressed':
        return '0' + str(2 + (pub[1] % 2)) + pyspecials.encode(pub[0], 16, 64)
    elif formt == 'bin_electrum':
        return pyspecials.encode(pub[0], 256, 32) + pyspecials.encode(pub[1], 256, 32)
    elif formt == 'hex_electrum':
        return pyspecials.encode(pub[0], 16, 64) + pyspecials.encode(pub[1], 16, 64)
    else:
        raise Exception("Invalid format!")


def decode_pubkey(pub, formt=None):
    if not formt:
        formt = get_pubkey_format(pub)

    if formt == 'decimal':
        return pub
    elif formt == 'bin':
        return (pyspecials.decode(pub[1:33], 256), pyspecials.decode(pub[33:65], 256))
    elif formt == 'bin_compressed':
        x = pyspecials.decode(pub[1:33], 256)
        beta = pow(int(x * x * x + A * x + B), int((P + 1) // 4), int(P))
        y = (P - beta) if ((beta + pyspecials.from_byte_to_int(pub[0])) % 2) else beta
        return (x, y)
    elif formt == 'hex':
        return (pyspecials.decode(pub[2:66], 16), pyspecials.decode(pub[66:130], 16))
    elif formt == 'hex_compressed':
        return decode_pubkey(pyspecials.safe_from_hex(pub), 'bin_compressed')
    elif formt == 'bin_electrum':
        return (pyspecials.decode(pub[:32], 256), pyspecials.decode(pub[32:64], 256))
    elif formt == 'hex_electrum':
        return (pyspecials.decode(pub[:64], 16), pyspecials.decode(pub[64:128], 16))
    else:
        raise Exception("Invalid format!")


def get_privkey_format(priv):
    if isinstance(priv, pyspecials.int_types):
        return 'decimal'
    elif len(priv) == 32:
        return 'bin'
    elif len(priv) == 33:
        return 'bin_compressed'
    elif len(priv) == 64:
        return 'hex'
    elif len(priv) == 66:
        return 'hex_compressed'
    else:
        bin_p = b58check_to_bin(priv)

    if len(bin_p) == 32:
        return 'wif'
    elif len(bin_p) == 33:
        return 'wif_compressed'
    else:
        raise Exception("WIF does not represent privkey")


def encode_privkey(priv, formt, vbyte=0):
    if not isinstance(priv, pyspecials.int_types):
        return encode_privkey(decode_privkey(priv), formt, vbyte)

    if formt == 'decimal':
        return priv
    elif formt == 'bin':
        return pyspecials.encode(priv, 256, 32)
    elif formt == 'bin_compressed':
        return pyspecials.encode(priv, 256, 32) + b'\x01'
    elif formt == 'hex':
        return pyspecials.encode(priv, 16, 64)
    elif formt == 'hex_compressed':
        return pyspecials.encode(priv, 16, 64) + '01'
    elif formt == 'wif':
        return pyspecials.bin_to_b58check(pyspecials.encode(priv, 256, 32),
                                          128 + int(vbyte))
    elif formt == 'wif_compressed':
        return pyspecials.bin_to_b58check(pyspecials.encode(priv, 256, 32) +
                                          b'\x01', 128 + int(vbyte))
    else:
        raise Exception("Invalid format!")


def decode_privkey(priv, formt=None):
    if not formt:
        formt = get_privkey_format(priv)

    if formt == 'decimal':
        return priv
    elif formt == 'bin':
        return pyspecials.decode(priv, 256)
    elif formt == 'bin_compressed':
        return pyspecials.decode(priv[:32], 256)
    elif formt == 'hex':
        return pyspecials.decode(priv, 16)
    elif formt == 'hex_compressed':
        return pyspecials.decode(priv[:64], 16)
    elif formt == 'wif':
        return pyspecials.decode(b58check_to_bin(priv), 256)
    elif formt == 'wif_compressed':
        return pyspecials.decode(b58check_to_bin(priv)[:32], 256)
    else:
        raise Exception("WIF does not represent privkey")


def add_pubkeys(p1, p2):
    f1, f2 = get_pubkey_format(p1), get_pubkey_format(p2)
    return encode_pubkey(fast_add(decode_pubkey(p1, f1), decode_pubkey(p2, f2)), f1)


def add_privkeys(p1, p2):
    f1, f2 = get_privkey_format(p1), get_privkey_format(p2)
    return encode_privkey((decode_privkey(p1, f1) + decode_privkey(p2, f2)) % N, f1)


def mul_privkeys(p1, p2):
    f1, f2 = get_privkey_format(p1), get_privkey_format(p2)
    return encode_privkey((decode_privkey(p1, f1) * decode_privkey(p2, f2)) % N, f1)


def multiply(pubkey, privkey):
    f1, f2 = get_pubkey_format(pubkey), get_privkey_format(privkey)
    pubkey, privkey = decode_pubkey(pubkey, f1), decode_privkey(privkey, f2)

    # http://safecurves.cr.yp.to/twist.html
    if not isinf(pubkey) and (pubkey[0] ** 3 + B - pubkey[1] * pubkey[1]) % P != 0:
        raise Exception("Point not on curve")

    return encode_pubkey(fast_multiply(pubkey, privkey), f1)


def divide(pubkey, privkey):
    factor = inv(decode_privkey(privkey), N)
    return multiply(pubkey, factor)


def compress(pubkey):
    f = get_pubkey_format(pubkey)

    if 'compressed' in f:
        return pubkey
    elif f == 'bin':
        return encode_pubkey(decode_pubkey(pubkey, f), 'bin_compressed')
    elif f == 'hex' or f == 'decimal':
        return encode_pubkey(decode_pubkey(pubkey, f), 'hex_compressed')


def decompress(pubkey):
    f = get_pubkey_format(pubkey)

    if 'compressed' not in f:
        return pubkey
    elif f == 'bin_compressed':
        return encode_pubkey(decode_pubkey(pubkey, f), 'bin')
    elif f == 'hex_compressed' or f == 'decimal':
        return encode_pubkey(decode_pubkey(pubkey, f), 'hex')


def privkey_to_pubkey(privkey):
    f = get_privkey_format(privkey)
    privkey = decode_privkey(privkey, f)
    if privkey >= N:
        raise Exception("Invalid privkey")
    if f in ['bin', 'bin_compressed', 'hex', 'hex_compressed', 'decimal']:
        return encode_pubkey(fast_multiply(G, privkey), f)
    else:
        return encode_pubkey(fast_multiply(G, privkey), f.replace('wif', 'hex'))


privtopub = privkey_to_pubkey


def neg_pubkey(pubkey):
    f = get_pubkey_format(pubkey)
    pubkey = decode_pubkey(pubkey, f)
    return encode_pubkey((pubkey[0], (P - pubkey[1]) % P), f)


def neg_privkey(privkey):
    f = get_privkey_format(privkey)
    privkey = decode_privkey(privkey, f)
    return encode_privkey((N - privkey) % N, f)


def subtract_pubkeys(p1, p2):
    f1, f2 = get_pubkey_format(p1), get_pubkey_format(p2)
    k2 = decode_pubkey(p2, f2)
    return encode_pubkey(fast_add(decode_pubkey(p1, f1), (k2[0], (P - k2[1]) % P)), f1)


def subtract_privkeys(p1, p2):
    f1, f2 = get_privkey_format(p1), get_privkey_format(p2)
    k2 = decode_privkey(p2, f2)
    return encode_privkey((decode_privkey(p1, f1) - k2) % N, f1)


# Hashes

def bin_hash160(string):
    intermed = hashlib.sha256(string).digest()
    digest = ''

    '''
    try:
        digest = hashlib.new('ripemd160', intermed).digest()
    except Exception:
        digest = RIPEMD160(intermed).digest()
    '''

    digest = hashlib.new('ripemd160', intermed).digest()

    return digest


def hash160(string):
    return pyspecials.safe_hexlify(bin_hash160(string))


def bin_sha256(string):
    binary_data = string if isinstance(string, bytes) else bytes(string, 'utf-8')
    return hashlib.sha256(binary_data).digest()


def sha256(string):
    return pyspecials.bytes_to_hex_string(bin_sha256(string))


'''
def bin_ripemd160(string):
    try:
        digest = hashlib.new('ripemd160', string).digest()
    except Exception:
        digest = RIPEMD160(string).digest()
    return digest


def ripemd160(string):
    return safe_hexlify(bin_ripemd160(string))
'''


def bin_dbl_sha256(s):
    bytes_to_hash = pyspecials.from_string_to_bytes(s)
    return hashlib.sha256(hashlib.sha256(bytes_to_hash).digest()).digest()


def dbl_sha256(string):
    return pyspecials.safe_hexlify(bin_dbl_sha256(string))


def bin_slowsha(string):
    string = pyspecials.from_string_to_bytes(string)
    orig_input = string
    for i in range(100000):
        string = hashlib.sha256(string + orig_input).digest()
    return string


def slowsha(string):
    return pyspecials.safe_hexlify(bin_slowsha(string))


def hash_to_int(x):
    if len(x) in [40, 64]:
        return pyspecials.decode(x, 16)
    return pyspecials.decode(x, 256)


def num_to_var_int(x):
    x = int(x)

    if x < 253:
        return pyspecials.from_int_to_byte(x)
    elif x < 65536:
        return pyspecials.from_int_to_byte(253) + pyspecials.encode(x, 256, 2)[::-1]
    elif x < 4294967296:
        return pyspecials.from_int_to_byte(254) + pyspecials.encode(x, 256, 4)[::-1]
    else:
        return pyspecials.from_int_to_byte(255) + pyspecials.encode(x, 256, 8)[::-1]


# WTF, Electrum?
def electrum_sig_hash(message):
    padded = b"\x18Bitcoin Signed Message:\n" + num_to_var_int(len(message))\
             + pyspecials.from_string_to_bytes(message)
    return bin_dbl_sha256(padded)


def random_key():
    # Gotta be secure after that java.SecureRandom fiasco...
    entropy = pyspecials.random_string(32) \
        + str(random.randrange(2**256)) \
        + str(int(time.time() * 1000000))
    return sha256(entropy)


def random_electrum_seed():
    # entropy = os.urandom(32) \ # fails in Python 3, hence copied from random_key()
    entropy = pyspecials.random_string(32) \
        + str(random.randrange(2**256)) \
        + str(int(time.time() * 1000000))
    return sha256(entropy)[:32]


# Encodings


def b58check_to_bin(inp):
    leadingzbytes = len(re.match('^1*', inp).group(0))
    data = b'\x00' * leadingzbytes + pyspecials.changebase(inp, 58, 256)
    assert bin_dbl_sha256(data[:-4])[:4] == data[-4:]
    return data[1:-4]


def get_version_byte(inp):
    leadingzbytes = len(re.match('^1*', inp).group(0))
    data = b'\x00' * leadingzbytes + pyspecials.changebase(inp, 58, 256)
    assert bin_dbl_sha256(data[:-4])[:4] == data[-4:]
    return ord(data[0])


def hex_to_b58check(inp, magicbyte=0):
    return pyspecials.bin_to_b58check(binascii.unhexlify(inp), magicbyte)


def b58check_to_hex(inp):
    return pyspecials.safe_hexlify(b58check_to_bin(inp))


def is_privkey(priv):
    try:
        get_privkey_format(priv)
        return True
    except Exception:
        return False


def is_pubkey(pubkey):
    try:
        get_pubkey_format(pubkey)
        return True
    except Exception:
        return False


def is_address(addr):
    ADDR_RE = re.compile("^[123mn][a-km-zA-HJ-NP-Z0-9]{26,33}$")
    return bool(ADDR_RE.match(addr))


# add/subtract
def add(p1, p2):
    if is_privkey(p1):
        return add_privkeys(p1, p2)
    else:
        return add_pubkeys(p1, p2)


def subtract(p1, p2):
    if is_privkey(p1):
        return subtract_privkeys(p1, p2)
    else:
        return subtract_pubkeys(p1, p2)
