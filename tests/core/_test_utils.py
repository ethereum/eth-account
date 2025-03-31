from typing import (
    List,
)

from eth_keys.datatypes import (
    Signature,
)
from hexbytes import (
    HexBytes,
)
from pydantic import (
    Field,
)

from eth_account.datastructures import (
    CustomPydanticModel,
    SignedSetCodeAuthorization,
)

TEST_SIGNED_AUTHORIZATION = SignedSetCodeAuthorization(
    chain_id=22,
    address=b"\x00" * 19 + b"\x01",
    nonce=1999,
    y_parity=1,
    r=123456789,
    s=987654321,
    signature=Signature(b"\x00" * 65),
    authorization_hash=HexBytes("0x"),
)
TEST_SIGNED_AUTHORIZATION_JSON = {
    "chainId": 22,
    "address": "0x" + "00" * 19 + "01",
    "nonce": 1999,
    "yParity": 1,
    "r": 123456789,
    "s": 987654321,
}
PYDANTIC_TEST_CLASS_JSON = {
    "intValue": 1,
    "nestedModel": {
        "intValue": 2,
        "strValue": "3",
        "authorizationList": [TEST_SIGNED_AUTHORIZATION_JSON],
    },
}


class PydanticTestClassInner(CustomPydanticModel):
    int_value: int = 2
    str_value: str = "3"
    authorization_list: List[SignedSetCodeAuthorization] = [TEST_SIGNED_AUTHORIZATION]
    excluded_field1: str = Field(default="4", exclude=True)
    excluded_field2: int = Field(default=5, exclude=True)


class PydanticTestClass(CustomPydanticModel):
    int_value: int = 1
    nested_model: PydanticTestClassInner = PydanticTestClassInner()
    excluded_field1: str = Field(default="6", exclude=True)
    excluded_field2: int = Field(default=7, exclude=True)
    excluded_field3: HexBytes = Field(default=HexBytes("0x08"), exclude=True)
