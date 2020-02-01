from .deterministic import (
    HDPath,
)
from .mnemonic import (
    Mnemonic,
)


def derive_ethereum_key(seed: bytes, account_index: int=0):
    return HDPath(f"m/44'/60'/0'/0/{account_index}").derive(seed)


def seed_from_mnemonic(words: str) -> bytes:
    Mnemonic.detect_language(words)
    return Mnemonic.to_seed(words)
