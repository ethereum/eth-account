import binascii
from bisect import (
    bisect_left,
)
import hashlib
import random


'''
This library was initially included from pybitcointools
https://github.com/vbuterin/pybitcointools/blob/aeb0a2bbb8bbfe421432d776c649650eaeb882a5/bitcoin/mnemonic.py
'''


def eint_to_bytes(entint, entbits):
    a = hex(entint)[2:].rstrip('L').zfill(32)
    print(a)
    return binascii.unhexlify(a)


def mnemonic_int_to_words(mint, mint_num_words, wordlist):
    backwords = [wordlist[(mint >> (11 * x)) & 0x7FF].strip() for x in range(mint_num_words)]
    return backwords[::-1]


def entropy_cs(entbytes):
    entropy_size = 8 * len(entbytes)
    checksum_size = entropy_size // 32
    hd = hashlib.sha256(entbytes).hexdigest()
    csint = int(hd, 16) >> (256 - checksum_size)
    return csint, checksum_size


# Call this to create a mnemonic phrase.
# Possible values for entbytes (entropy bytes) are 16, 20, 24, 28 and 32
def entropy_to_words(entbytes, wordlist):
    if len(entbytes) not in [16, 20, 24, 28, 32]:
        raise ValueError("entropy must be an element of [16, 20, 24, 28, 32]")

    entropy_size = 8 * len(entbytes)
    csint, checksum_size = entropy_cs(entbytes)
    entint = int(binascii.hexlify(entbytes), 16)
    mint = (entint << checksum_size) | csint
    mint_num_words = (entropy_size + checksum_size) // 11

    return mnemonic_int_to_words(mint, mint_num_words, wordlist)


def words_bisect(word, wordlist):
    lo = bisect_left(wordlist, word)
    hi = len(wordlist) - bisect_left(wordlist[:lo:-1], word)

    return lo, hi


def words_split(wordstr, wordlist):
    def popword(wordstr, wordlist):
        for fwl in range(1, 9):
            w = wordstr[:fwl].strip()
            lo, hi = words_bisect(w, wordlist)

            if(hi - lo == 1):
                return w, wordstr[fwl:].lstrip()

            wordlist = wordlist[lo:hi]

        raise Exception("Wordstr %s not found in list" % w)

    words = []
    tail = wordstr

    while(len(tail)):
        head, tail = popword(tail, wordlist)
        words.append(head)

    return words


def words_to_mnemonic_int(words, wordlist):
    if(isinstance(words, str)):
        words = words_split(words, wordlist)
    return sum([wordlist.index(w) << (11 * x) for x, w in enumerate(words[::-1])])


# BIP32 checksum verification
def words_verify(words, wordlist):
    if(isinstance(words, str)):
        words = words_split(words, wordlist)

    mint = words_to_mnemonic_int(words, wordlist)
    mint_bits = len(words) * 11
    cs_bits = mint_bits // 32
    entropy_bits = mint_bits - cs_bits
    eint = mint >> cs_bits
    csint = mint & ((1 << cs_bits) - 1)
    ebytes = eint_to_bytes(eint, entropy_bits)
    return csint == entropy_cs(ebytes)


# Derive a root seed which can be used to derive the master private key and chaincode
def mnemonic_to_seed(mnemonic_phrase, passphrase=b''):
    try:
        from hashlib import pbkdf2_hmac

        def pbkdf2_hmac_sha512(password, salt, iters=2048):
            return pbkdf2_hmac(hash_name='sha512', password=password,
                               salt=salt, iterations=iters)
    except ImportError:
        try:
            from Crypto.Protocol.KDF import PBKDF2
            from Crypto.Hash import SHA512, HMAC

            def pbkdf2_hmac_sha512(password, salt, iters=2048):
                return PBKDF2(password=password, salt=salt, dkLen=64,
                              count=iters, prf=lambda p, s:
                              HMAC.new(p, s, SHA512).digest())
        except ImportError:
            try:
                from pbkdf2 import PBKDF2
                import hmac

                def pbkdf2_hmac_sha512(password, salt, iters=2048):
                    return PBKDF2(password, salt, iterations=iters,
                                  macmodule=hmac,
                                  digestmodule=hashlib.sha512).read(64)

            except ImportError:
                raise RuntimeError("No implementation of pbkdf2 was found!")

    return pbkdf2_hmac_sha512(password=mnemonic_phrase,
                              salt=b'mnemonic' + passphrase)


# Relevant for Electrum style mnemonics
def words_mine(prefix, entbits, satisfunction, wordlist,
               randombits=random.getrandbits):
    prefix_bits = len(prefix) * 11
    mine_bits = entbits - prefix_bits
    pint = words_to_mnemonic_int(prefix, wordlist)
    pint <<= mine_bits
    dint = randombits(mine_bits)
    count = 0

    while(not satisfunction(entropy_to_words(eint_to_bytes(pint + dint, entbits)))):
        dint = randombits(mine_bits)

        if((count & 0xFFFF) == 0):
            print("Searched %f percent of the space" %
                  (float(count) / float(1 << mine_bits)))

    return entropy_to_words(eint_to_bytes(pint + dint, entbits))


if __name__ == "__main__":
    import json
    import os
    thisdir = os.path.dirname(os.path.realpath(__file__))
    vectors = os.path.join(thisdir, "vectors.json")
    wordlist = os.path.join(thisdir, "wordlist/bip39_english.txt")
    testvectors = json.load(open(vectors, 'r'))
    passed = True

    with open(wordlist, 'r') as fwordlist:
        wlcnt = fwordlist.readlines()

    for v in testvectors['english']:
        ebytes = binascii.unhexlify(v[0])
        w = ' '.join(entropy_to_words(ebytes, wlcnt))
        seed = mnemonic_to_seed(w.encode("utf-8"), 'TREZOR'.encode("utf-8"))
        # print("our seed: %s" % binascii.hexlify(seed).decode("utf-8"))
        # print("testvector: %s" % v[2])
        passed = passed and w == v[1]
        passed = passed and binascii.hexlify(seed).decode("utf-8") == v[2]

    print("Test %s" % ("Passed" if passed else "Failed"))
