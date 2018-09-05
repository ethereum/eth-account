import hashlib
import hmac

from eth_account.hdaccount import (
    pyspecials,
    utils,
)

# from binascii import unhexlify
# Electrum wallets


'''
This library was included from pybitcointools
https://github.com/vbuterin/pybitcointools/blob/aeb0a2bbb8bbfe421432d776c649650eaeb882a5/bitcoin/deterministic.py
'''

'''

def electrum_stretch(seed):
    return utils.slowsha(seed)

# Accepts seed or stretched seed, returns master public key


def electrum_mpk(seed):
    if len(seed) == 32:
        seed = electrum_stretch(seed)
    return utils.privkey_to_pubkey(seed)[2:]

# Accepts (seed or stretched seed), index and secondary index
# (conventionally 0 for ordinary addresses, 1 for change) , returns privkey


def electrum_privkey(seed, n, for_change=0):
    if len(seed) == 32:
        seed = electrum_stretch(seed)

    mpk = electrum_mpk(seed)
    offset = utils.dbl_sha256(pyspecials.from_int_representation_to_bytes(n) + b':' +
                              pyspecials.from_int_representation_to_bytes(for_change) +
                              b':' + unhexlify(mpk))
    return utils.add_privkeys(seed, offset)

# Accepts (seed or stretched seed or master pubkey), index and secondary index
# (conventionally 0 for ordinary addresses, 1 for change) , returns pubkey


def electrum_pubkey(masterkey, n, for_change=0):
    if len(masterkey) == 32:
        mpk = electrum_mpk(electrum_stretch(masterkey))
    elif len(masterkey) == 64:
        mpk = electrum_mpk(masterkey)
    else:
        mpk = masterkey

    bin_mpk = utils.encode_pubkey(mpk, 'bin_electrum')
    offset = pyspecials.bin_dbl_sha256(pyspecials.from_int_representation_to_bytes(n) + b':' +
                                       pyspecials.from_int_representation_to_bytes(for_change) +
                                       b':' + bin_mpk)
    return utils.add_pubkeys('04' + mpk, utils.privtopub(offset))

# seed/stretched seed/pubkey -> address (convenience method)


def electrum_address(masterkey, n, for_change=0, version=0):
    return utils.pubkey_to_address(electrum_pubkey(masterkey, n, for_change), version)


# Given a master public key, a private key from that wallet and its index,
# cracks the secret exponent which can be used to generate all other private
# keys in the wallet


def crack_electrum_wallet(mpk, pk, n, for_change=0):
    bin_mpk = utils.encode_pubkey(mpk, 'bin_electrum')
    offset = utils.dbl_sha256(str(n) + ':' + str(for_change) + ':' + bin_mpk)
    return utils.subtract_privkeys(pk, offset)

'''

# Below code ASSUMES binary inputs and compressed pubkeys
MAINNET_PRIVATE = b'\x04\x88\xAD\xE4'
MAINNET_PUBLIC = b'\x04\x88\xB2\x1E'
TESTNET_PRIVATE = b'\x04\x35\x83\x94'
TESTNET_PUBLIC = b'\x04\x35\x87\xCF'
PRIVATE = [MAINNET_PRIVATE, TESTNET_PRIVATE]
PUBLIC = [MAINNET_PUBLIC, TESTNET_PUBLIC]

# BIP32 child key derivation


def raw_bip32_ckd(rawtuple, i):
    vbytes, depth, fingerprint, oldi, chaincode, key = rawtuple
    i = int(i)

    if vbytes in PRIVATE:
        priv = key
        pub = utils.privtopub(key)
    else:
        pub = key

    if i >= 2**31:
        if vbytes in PUBLIC:
            raise Exception("Can't do private derivation on public key!")
        hmac_res = hmac.new(chaincode, b'\x00' + priv[:32] + pyspecials.encode(i, 256, 4),
                            hashlib.sha512).digest()
    else:
        hmac_res = hmac.new(chaincode, pub + pyspecials.encode(i, 256, 4), hashlib.sha512).digest()

    if vbytes in PRIVATE:
        newkey = utils.add_privkeys(hmac_res[:32] + B'\x01', priv)
        fingerprint = utils.bin_hash160(utils.privtopub(key))[:4]
    if vbytes in PUBLIC:
        newkey = utils.add_pubkeys(utils.compress(utils.privtopub(hmac_res[:32])), key)
        fingerprint = utils.bin_hash160(key)[:4]

    return (vbytes, depth + 1, fingerprint, i, hmac_res[32:], newkey)


def raw_bip32_privtopub(rawtuple):
    vbytes, depth, fingerprint, i, chaincode, key = rawtuple

    if vbytes in PUBLIC:
        return (vbytes, depth, fingerprint, i, chaincode, key)

    newvbytes = MAINNET_PUBLIC if vbytes == MAINNET_PRIVATE else TESTNET_PUBLIC
    return (newvbytes, depth, fingerprint, i, chaincode, utils.privtopub(key))


def raw_crack_bip32_privkey(parent_pub, priv):
    vbytes, depth, fingerprint, i, chaincode, key = priv
    pvbytes, pdepth, pfingerprint, pi, pchaincode, pkey = parent_pub
    i = int(i)

    if i >= 2**31:
        raise Exception("Can't crack private derivation!")

    hmac_res = hmac.new(pchaincode, pkey + pyspecials.encode(i, 256, 4), hashlib.sha512).digest()

    pprivkey = utils.subtract_privkeys(key, hmac_res[:32] + b'\x01')

    newvbytes = MAINNET_PRIVATE if vbytes == MAINNET_PUBLIC else TESTNET_PRIVATE
    return (newvbytes, pdepth, pfingerprint, pi, pchaincode, pprivkey)


def bip32_serialize(rawtuple):
    vbytes, depth, fingerprint, i, chaincode, key = rawtuple
    i = pyspecials.encode(i, 256, 4)
    chaincode = pyspecials.encode(utils.hash_to_int(chaincode), 256, 32)
    keydata = b'\x00' + key[:-1] if vbytes in PRIVATE else key
    bindata = vbytes + pyspecials.from_int_to_byte(depth % 256) + fingerprint + i + \
        chaincode + keydata
    return pyspecials.changebase(bindata + pyspecials.bin_dbl_sha256(bindata)[:4], 256, 58)


def bip32_deserialize(data):
    dbin = pyspecials.changebase(data, 58, 256)

    if pyspecials.bin_dbl_sha256(dbin[:-4])[:4] != dbin[-4:]:
        raise Exception("Invalid checksum")

    vbytes = dbin[0:4]
    depth = pyspecials.from_byte_to_int(dbin[4])
    fingerprint = dbin[5:9]
    i = pyspecials.decode(dbin[9:13], 256)
    chaincode = dbin[13:45]
    key = dbin[46:78] + b'\x01' if vbytes in PRIVATE else dbin[45:78]
    return (vbytes, depth, fingerprint, i, chaincode, key)


def bip32_privtopub(data):
    return bip32_serialize(raw_bip32_privtopub(bip32_deserialize(data)))


# Use this for child derivation. Input BIP32 serialized key and index
def bip32_ckd(data, i):
    return bip32_serialize(raw_bip32_ckd(bip32_deserialize(data), i))


def bip32_master_key(seed, vbytes=MAINNET_PRIVATE):
    hmac_res = hmac.new(pyspecials.from_string_to_bytes("Bitcoin seed"),
                        pyspecials.from_string_to_bytes(seed),
                        hashlib.sha512).digest()
    return bip32_serialize((vbytes, 0, b'\x00' * 4, 0, hmac_res[32:], hmac_res[:32] + b'\x01'))


def bip32_bin_extract_key(data):
    return bip32_deserialize(data)[-1]


def bip32_extract_key(data):
    return pyspecials.safe_hexlify(bip32_deserialize(data)[-1])


'''
def bip32_descend(*args):
    if len(args) == 2 and isinstance(args[1], list):
        key, path = args
    else:
        key, path = args[0], map(int, args[1:])

    for p in path:
        key = bip32_ckd(key, p)

    return bip32_extract_key(key)
'''

# Exploits the same vulnerability as above in Electrum wallets
# Takes a BIP32 pubkey and one of the child privkeys of its corresponding
# privkey and returns the BIP32 privkey associated with that pubkey


'''
def crack_bip32_privkey(parent_pub, priv):
    dsppub = bip32_deserialize(parent_pub)
    dspriv = bip32_deserialize(priv)
    return bip32_serialize(raw_crack_bip32_privkey(dsppub, dspriv))


def coinvault_pub_to_bip32(*args):
    if len(args) == 1:
        args = args[0].split(' ')
    vals = map(int, args[34:])
    I1 = ''.join(map(chr, vals[:33]))
    I2 = ''.join(map(chr, vals[35:67]))
    return bip32_serialize((MAINNET_PUBLIC, 0, b'\x00' * 4, 0, I2, I1))


def coinvault_priv_to_bip32(*args):
    if len(args) == 1:
        args = args[0].split(' ')
    vals = map(int, args[34:])
    I2 = ''.join(map(chr, vals[35:67]))
    I3 = ''.join(map(chr, vals[72:104]))
    return bip32_serialize((MAINNET_PRIVATE, 0, b'\x00' * 4, 0, I2, I3 + b'\x01'))
'''
