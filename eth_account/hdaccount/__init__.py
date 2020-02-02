from .deterministic import (
    HDPath,
)
from .mnemonic import (
    Mnemonic,
)

ETHEREUM_BASE_PATH = "m/44'/60'/0'/0"


def derive_ethereum_key(seed: bytes, account_index: int=0):
    return HDPath(f"{ETHEREUM_BASE_PATH}/{account_index}").derive(seed)


def seed_from_mnemonic(words: str, passphrase="") -> bytes:
    lang = Mnemonic.detect_language(words)
    if not Mnemonic(lang).is_mnemonic_valid(words):
        raise ValueError(
            f"Provided words: '{words}', are not a valid BIP39 mnemonic phrase!"
        )
    return Mnemonic.to_seed(words, passphrase)


def mnemonic_from_entropy(entropy: bytes, lang="english") -> str:
    return Mnemonic(lang).to_mnemonic(entropy)
