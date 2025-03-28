from typing import (
    Any,
    Dict,
    NamedTuple,
    SupportsIndex,
    Tuple,
    Type,
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
    to_checksum_address,
)
from hexbytes import (
    HexBytes,
)
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
)
from pydantic.alias_generators import (
    to_camel,
)
from pydantic.json_schema import (
    DEFAULT_REF_TEMPLATE,
    GenerateJsonSchema,
    JsonSchemaMode,
    JsonSchemaValue,
)
from pydantic_core import (
    CoreSchema,
    PydanticOmit,
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


class OmitJsonSchema(GenerateJsonSchema):
    def handle_invalid_for_json_schema(
        self, schema: CoreSchema, error_info: str
    ) -> JsonSchemaValue:
        raise PydanticOmit


class CustomPydanticModel(BaseModel):
    """
    A base class for eth-account pydantic models that provides custom JSON-RPC
    serialization configuration. JSON-RPC serialization is configured to use
    camelCase keys and to exclude fields that are marked as ``exclude=True``. To
    serialize a model to the expected JSON-RPC format, use
    ``model_dump(by_alias=True)``.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,  # populate by snake_case (python) args
        alias_generator=to_camel,  # serialize by camelCase (json-rpc) keys
    )

    def recursive_model_dump(self) -> Any:
        # TODO: Remove in next major release. This was introduced because of a bug with
        #  a ``@field_serializer`` decorator not being applied correctly to nested
        #  models. This is no longer necessary.
        warnings.warn(
            "recursive_model_dump() is deprecated. Please use "
            "model_dump(by_alias=True) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.model_dump(by_alias=True)

    @classmethod
    def model_json_schema(
        cls,
        by_alias: bool = True,
        ref_template: str = DEFAULT_REF_TEMPLATE,
        # default to ``OmitJsonSchema`` to prevent errors from excluded fields
        schema_generator: Type[GenerateJsonSchema] = OmitJsonSchema,
        mode: JsonSchemaMode = "validation",
    ) -> Dict[str, Any]:
        """
        Omits excluded fields from the JSON schema, preventing errors that would
        otherwise be raised by the default schema generator.
        """
        return super().model_json_schema(
            by_alias=by_alias,
            ref_template=ref_template,
            schema_generator=schema_generator,
            mode=mode,
        )


class SignedSetCodeAuthorization(CustomPydanticModel):
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
