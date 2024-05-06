import warnings

from eth_account.typed_transactions import (
    AccessListTransaction,
    BlobTransaction,
    DynamicFeeTransaction,
    TypedTransaction,
)

warnings.warn(
    "Typed transactions will no longer be imported from _utils. "
    "Import from eth_account.typed_transactions instead",
    DeprecationWarning,
    stacklevel=2,
)
