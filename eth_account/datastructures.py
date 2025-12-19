from typing import (
    Any,
    NamedTuple,
    SupportsIndex,
    overload,
)

from eth_keys.datatypes import (
    Signature,
)
from eth_typing import (
    ChecksumAddress,
)
from eth_utils import (
    CamelModel,
    to_checksum_address,
)
from hexbytes import (
    HexBytes,
)
from pydantic import (
    Field,
    field_serializer,
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
    def __getitem__(self, index: slice) -> tuple[Any, ...]:
        ...

    @overload
    def __getitem__(self, index: str) -> Any:
        ...

    def __getitem__(self, index: SupportsIndex | slice | str) -> Any:
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
    def __getitem__(self, index: slice) -> tuple[Any, ...]:
        ...

    @overload
    def __getitem__(self, index: str) -> Any:
        ...

    def __getitem__(self, index: SupportsIndex | slice | str) -> Any:
        if isinstance(index, (int, slice)):
            return super().__getitem__(index)
        elif isinstance(index, str):
            return getattr(self, index)
        else:
            raise TypeError("Index must be an integer, slice, or string")


class SignedSetCodeAuthorization(CamelModel):
    chain_id: int
    address: bytes
    nonce: int
    y_parity: int
    r: int
    s: int
    signature: Signature = Field(exclude=True)
    authorization_hash: HexBytes = Field(exclude=True)

    @field_serializer("address")
    @classmethod
    def serialize_address(cls, value: bytes) -> ChecksumAddress:
        return to_checksum_address(value)

    @property
    def authority(self) -> bytes:
        """
        Return the address of the authority that signed the authorization.

        In order to prevent any potential confusion or mal-intent, the authority is
        always derived from the signature and the authorization hash, rather than
        statically assigned. This value should be verified against the expected
        authority for a signed authorization.
        """
        return self.signature.recover_public_key_from_msg_hash(
            self.authorization_hash
        ).to_canonical_address()
