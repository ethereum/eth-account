from typing import (
    NamedTuple,
)
import warnings

from hexbytes import (
    HexBytes,
)


def __getitem__(self, index):
    try:
        return tuple.__getitem__(self, index)
    except TypeError:
        return getattr(self, index)


class SignedTransaction(
    NamedTuple(
        "SignedTransaction",
        [
            ("rawTransaction", HexBytes),
            ("raw_transaction", HexBytes),
            ("hash", HexBytes),
            ("r", int),
            ("s", int),
            ("v", int),
        ],
    )
):
    rawTransaction: HexBytes
    raw_transaction: HexBytes
    hash: HexBytes
    r: int
    s: int
    v: int

    def __getattribute__(cls, name):
        if name == "rawTransaction":
            warnings.warn(
                "The attribute rawTransaction on SignedTransaction is deprecated "
                "in favor of raw_transaction",
                DeprecationWarning,
                stacklevel=2,
            )
        return super().__getattribute__(name)

    def __getitem__(self, index):
        return __getitem__(self, index)


class SignedMessage(
    NamedTuple(
        "SignedMessage",
        [
            ("messageHash", HexBytes),
            ("message_hash", HexBytes),
            ("r", int),
            ("s", int),
            ("v", int),
            ("signature", HexBytes),
        ],
    )
):
    messageHash: HexBytes
    message_hash: HexBytes
    r: int
    s: int
    v: int
    signature: HexBytes

    def __getattribute__(cls, name):
        if name == "messageHash":
            warnings.warn(
                "The attribute messageHash on SignedMessage is deprecated "
                "in favor of message_hash",
                DeprecationWarning,
                stacklevel=2,
            )
        return super().__getattribute__(name)

    def __getitem__(self, index):
        return __getitem__(self, index)
