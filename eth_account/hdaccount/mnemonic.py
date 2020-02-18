# Originally from: https://github.com/trezor/python-mnemonic
#
# Copyright (c) 2013 Pavol Rusnak
# Copyright (c) 2017 mruddy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import binascii
import hashlib
import os
from pathlib import (
    Path,
)
import unicodedata

from eth_utils import (
    ValidationError,
    combomethod,
)

PBKDF2_ROUNDS = 2048
VALID_ENTROPY_SIZES = [16, 20, 24, 28, 32]
VALID_WORD_COUNTS = [12, 15, 18, 21, 24]
WORDLIST_DIR = Path(__file__).parent / "wordlist"
WORDLIST_LEN = 2048

_cached_wordlists = dict()


def get_wordlist(language):
    if language in _cached_wordlists.keys():
        return _cached_wordlists[language]
    with open(WORDLIST_DIR / f"{language}.txt", "r", encoding="utf-8") as f:
        wordlist = [w.strip() for w in f.readlines()]
    if len(wordlist) != WORDLIST_LEN:
        raise ValidationError(
            f"Wordlist should contain {WORDLIST_LEN} words, "
            f"but it contains {len(wordlist)} words."
        )
    _cached_wordlists[language] = wordlist
    return wordlist


def normalize_string(txt):
    if isinstance(txt, bytes):
        utxt = txt.decode("utf8")
    elif isinstance(txt, str):
        utxt = txt
    else:
        raise ValidationError("String value expected")

    return unicodedata.normalize("NFKD", utxt)


class Mnemonic(object):
    def __init__(self, language):
        if language not in Mnemonic.list_languages():
            raise ValidationError(
                f'Invalid language choice "{language}", must be one of {self.list_langauges()}'
            )
        self.language = language
        self.wordlist = get_wordlist(language)

    @staticmethod
    def list_languages():
        return sorted(Path(f).stem for f in WORDLIST_DIR.rglob("*.txt"))

    @classmethod
    def detect_language(cls, raw_mnemonic):
        mnemonic = normalize_string(raw_mnemonic)

        words = set(mnemonic.split(" "))
        matching_languages = {
            lang
            for lang in Mnemonic.list_languages()
            if len(words.intersection(cls(lang).wordlist)) == len(words)
        }

        # No language had all words match it, so the language can't be fully determined
        if len(matching_languages) < 1:
            raise ValidationError(f"Language not detected for word(s): {raw_mnemonic}")

        # If both chinese simplified and chinese traditional match (because one is a subset of the
        # other) then return simplified. This doesn't hold for other languages.
        if len(matching_languages) == 2 and all("chinese" in lang for lang in matching_languages):
            return "chinese_simplified"

        # Because certain wordlists share some similar words, if we detect multiple languages
        # that the provided mnemonic word(s) could be valid in, we have to throw
        if len(matching_languages) > 1:
            raise ValidationError(f"Word(s) are valid in multiple languages: {raw_mnemonic}")

        (language,) = matching_languages
        return language

    def generate(self, num_words=12):
        if num_words not in VALID_WORD_COUNTS:
            raise ValidationError(
                f"Invalid choice for number of words: {num_words}, should be one of "
                f"{VALID_WORD_COUNTS}"
            )
        return self.to_mnemonic(os.urandom(4 * num_words // 3))  # 4/3 bytes per word

    def to_mnemonic(self, entropy):
        if len(entropy) not in VALID_ENTROPY_SIZES:
            raise ValidationError(
                f"Invalid data length {len(entropy)}, should be one of "
                f"{VALID_ENTROPY_SIZES}"
            )
        checksum = hashlib.sha256(entropy).hexdigest()
        bits = (
            bin(int(binascii.hexlify(entropy), 16))[2:].zfill(len(entropy) * 8) +
            bin(int(checksum, 16))[2:].zfill(256)[: len(entropy) * 8 // 32]
        )
        result = []
        for i in range(len(bits) // 11):
            idx = int(bits[i * 11: (i + 1) * 11], 2)
            result.append(self.wordlist[idx])
        if self.language == "japanese":  # Japanese must be joined by ideographic space.
            result_phrase = u"\u3000".join(result)
        else:
            result_phrase = " ".join(result)
        return result_phrase

    def check(self, mnemonic):
        words = normalize_string(mnemonic).split(" ")
        # list of valid mnemonic lengths
        if len(words) not in VALID_WORD_COUNTS:
            return False
        try:
            idx = map(lambda x: bin(self.wordlist.index(x))[2:].zfill(11), words)
            encoded_seed = "".join(idx)
        except ValidationError:
            return False
        l = len(encoded_seed)  # noqa: E741
        bits = encoded_seed[: l // 33 * 32]
        stored_checksum = encoded_seed[-l // 33:]
        raw_seed = binascii.unhexlify(hex(int(bits, 2))[2:].rstrip("L").zfill(l // 33 * 8))
        checksum = bin(int(hashlib.sha256(raw_seed).hexdigest(), 16))[2:].zfill(256)[: l // 33]
        return stored_checksum == checksum

    def expand_word(self, prefix):
        if prefix in self.wordlist:
            return prefix
        else:
            matches = [word for word in self.wordlist if word.startswith(prefix)]
            if len(matches) == 1:  # matched exactly one word in the wordlist
                return matches[0]
            else:
                # exact match not found.
                # this is not a validation routine, just return the input
                return prefix

    def expand(self, mnemonic):
        return " ".join(map(self.expand_word, mnemonic.split(" ")))

    @classmethod
    def to_seed(cls, checked_mnemonic: str, passphrase: str="") -> bytes:
        """
        :param str checked_mnemonic: Must be a correct, fully-expanded BIP39 seed phrase.
        :param str passphrase: Encryption passphrase used to secure the mnemonic.
        :returns bytes: 64 bytes of raw seed material from PRNG
        """
        mnemonic = normalize_string(checked_mnemonic)
        # NOTE: This domain separater ("mnemonic") is added per BIP39 spec to the passphrase
        # https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki#from-mnemonic-to-seed
        salt = "mnemonic" + normalize_string(passphrase)
        # From BIP39:
        #   To create a binary seed from the mnemonic, we use the PBKDF2 function with a
        # mnemonic sentence (in UTF-8 NFKD) used as the password and the string "mnemonic"
        # and passphrase (again in UTF-8 NFKD) used as the salt.
        stretched = hashlib.pbkdf2_hmac(
            "sha512",
            mnemonic.encode("utf-8"),
            salt.encode("utf-8"),
            PBKDF2_ROUNDS,
        )
        return stretched[:64]
