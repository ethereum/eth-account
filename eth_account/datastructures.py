from typing import (
    Any,
    NamedTuple,
    SupportsIndex,
    Tuple,
    Union,
    overload,
)

from hexbytes import (
    HexBytes,
)


class SignedTransaction(
    NamedTuple(
        "SignedTransaction",
        [
            ("raw_transaction", HexBytes),
            ("hash", HexBytes),
            ("r", int),
            ("s", int),
            ("v", int),
        ],
    )
):
    @overload
    def __getitem__(self, index: SupportsIndex) -> Any:
        ...

    @overload
    def __getitem__(self, index: slice) -> Tuple[Any, ...]:
        ...

    @overload
    def __getitem__(self, index: str) -> Any:
        ...

    def __getitem__(self, index: Union[SupportsIndex, slice, str]) -> Any:
        if isinstance(index, (int, slice)):
            return super().__getitem__(index)
        elif isinstance(index, str):
            return getattr(self, index)
        else:
            raise TypeError("Index must be an integer, slice, or string")


class SignedMessage(
    NamedTuple(
        "SignedMessage",
        [
            ("message_hash", HexBytes),
            ("r", int),
            ("s", int),
            ("v", int),
            ("signature", HexBytes),
        ],
    )
):
    @overload
    def __getitem__(self, index: SupportsIndex) -> Any:
        ...

    @overload
    def __getitem__(self, index: slice) -> Tuple[Any, ...]:
        ...

    @overload
    def __getitem__(self, index: str) -> Any:
        ...

    def __getitem__(self, index: Union[SupportsIndex, slice, str]) -> Any:
        if isinstance(index, (int, slice)):
            return super().__getitem__(index)
        elif isinstance(index, str):
            return getattr(self, index)
        else:
            raise TypeError("Index must be an integer, slice, or string")
