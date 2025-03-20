from typing import (
    Any,
    NamedTuple,
    SupportsIndex,
    Tuple,
    Union,
    cast,
    overload,
)

from eth_keys.datatypes import (
    Signature,
)
from eth_typing import (
    HexStr,
)
from eth_utils import (
    to_checksum_address,
)
from hexbytes import (
    HexBytes,
)
from pydantic import (
    BaseModel,
    ConfigDict,
    field_serializer,
)
from pydantic.alias_generators import (
    to_camel,
)

from eth_account.types import (
    SignedAuthorizationDict,
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


class SignedSetCodeAuthorization(BaseModel):
    chain_id: int
    address: bytes
    nonce: int
    y_parity: int
    r: int
    s: int
    signature: Signature
    authorization_hash: HexBytes

    _excludes = {"signature", "authorization_hash", "authority"}

    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # `Signature` is not a standard type
        populate_by_name=True,  # populate using snake_case
        alias_generator=to_camel,
    )

    @field_serializer("address", when_used="json")
    @classmethod
    def serialize_address(cls, value: bytes) -> str:
        return to_checksum_address(value)

    @field_serializer("r", "s", when_used="json")
    @classmethod
    def serialize_bigint_as_hex(cls, value: int) -> HexStr:
        return HexStr(hex(value))

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

    def as_rpc_object(self) -> SignedAuthorizationDict:
        return cast(
            SignedAuthorizationDict,
            self.model_dump(mode="json", by_alias=True, exclude=self._excludes),
        )
