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
import unicodedata

PBKDF2_ROUNDS = 2048


class ConfigurationError(Exception):
    pass


class Mnemonic(object):
    def __init__(self, language):
        self.radix = 2048
        with open(f"{self._get_directory()}/{language}.txt", "r", encoding="utf-8") as f:
            self.wordlist = [w.strip() for w in f.readlines()]
        if len(self.wordlist) != self.radix:
            raise ConfigurationError(
                f"Wordlist should contain {self.radix} words, "
                f"but it contains {len(self.wordlist)} words."
            )

    @classmethod
    def _get_directory(cls):
        return os.path.join(os.path.dirname(__file__), "wordlist")

    @classmethod
    def list_languages(cls):
        return [
            f.split(".")[0]
            for f in os.listdir(cls._get_directory())
            if f.endswith(".txt")
        ]

    @classmethod
    def normalize_string(cls, txt):
        if isinstance(txt, bytes):
            utxt = txt.decode("utf8")
        elif isinstance(txt, str):
            utxt = txt
        else:
            raise TypeError("String value expected")

        return unicodedata.normalize("NFKD", utxt)

    @classmethod
    def detect_language(cls, code):
        code = cls.normalize_string(code)
        first = code.split(" ")[0]
        languages = cls.list_languages()

        for lang in languages:
            mnemo = cls(lang)
            if first in mnemo.wordlist:
                return lang

        raise ConfigurationError("Language not detected")

    def generate(self, strength=128):
        if strength not in [128, 160, 192, 224, 256]:
            raise ValueError(
                "Strength should be one of the following: [128, 160, 192, 224, 256]"
            )
        return self.to_mnemonic(os.urandom(strength // 8))

    def to_mnemonic(self, data):
        if len(data) not in [16, 20, 24, 28, 32]:
            raise ValueError(
                "Data length should be one of the following: [16, 20, 24, 28, 32]"
                % len(data)
            )
        h = hashlib.sha256(data).hexdigest()
        b = (
            bin(int(binascii.hexlify(data), 16))[2:].zfill(len(data) * 8) +
            bin(int(h, 16))[2:].zfill(256)[: len(data) * 8 // 32]
        )
        result = []
        for i in range(len(b) // 11):
            idx = int(b[i * 11: (i + 1) * 11], 2)
            result.append(self.wordlist[idx])
        if (
            self.detect_language(" ".join(result)) == "japanese"
        ):  # Japanese must be joined by ideographic space.
            result_phrase = u"\u3000".join(result)
        else:
            result_phrase = " ".join(result)
        return result_phrase

    def check(self, mnemonic):
        mnemonic = self.normalize_string(mnemonic).split(" ")
        # list of valid mnemonic lengths
        if len(mnemonic) not in [12, 15, 18, 21, 24]:
            return False
        try:
            idx = map(lambda x: bin(self.wordlist.index(x))[2:].zfill(11), mnemonic)
            b = "".join(idx)
        except ValueError:
            return False
        l = len(b)  # noqa: E741
        d = b[: l // 33 * 32]
        h = b[-l // 33:]
        nd = binascii.unhexlify(hex(int(d, 2))[2:].rstrip("L").zfill(l // 33 * 8))
        nh = bin(int(hashlib.sha256(nd).hexdigest(), 16))[2:].zfill(256)[: l // 33]
        return h == nh

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
    def to_seed(cls, mnemonic, passphrase=""):
        mnemonic = cls.normalize_string(mnemonic)
        passphrase = cls.normalize_string(passphrase)
        passphrase = "mnemonic" + passphrase
        mnemonic = mnemonic.encode("utf-8")
        passphrase = passphrase.encode("utf-8")
        stretched = hashlib.pbkdf2_hmac("sha512", mnemonic, passphrase, PBKDF2_ROUNDS)
        return stretched[:64]
