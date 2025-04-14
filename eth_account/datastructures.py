from typing import (
    Any,
    Dict,
    NamedTuple,
    SupportsIndex,
    Tuple,
    Union,
    overload,
)
import warnings

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


class CustomPydanticModel(CamelModel):
    # TODO: remove this intermediary class in the next major release
    """
    A base class for eth-account pydantic models that provides custom JSON-RPC
    serialization configuration. JSON-RPC serialization is configured to use
    camelCase keys and to exclude fields that are marked as ``exclude=True``. To
    serialize a model to the expected JSON-RPC format, use
    ``model_dump(by_alias=True)``.
    """

    def recursive_model_dump(self) -> Dict[str, Any]:
        warnings.warn(
            "recursive_model_dump() is deprecated. Please use "
            "model_dump(by_alias=True) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.model_dump(by_alias=True)


class SignedSetCodeAuthorization(CustomPydanticModel):
    # TODO: inherit from ``CamelModel`` in the next major release
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
