import pytest
import json

from pydantic.alias_generators import (
    to_camel,
)

from tests.core._test_utils import (
    TEST_SIGNED_AUTHORIZATION,
    PydanticTestClass,
)


@pytest.mark.parametrize(
    "pydantic_model,expected",
    (
        (
            TEST_SIGNED_AUTHORIZATION,
            {
                "chainId": 22,
                "address": "0x" + "00" * 19 + "01",
                "nonce": 1999,
                "yParity": 1,
                "r": 123456789,
                "s": 987654321,
            },
        ),
        (
            PydanticTestClass(),
            {
                "intValue": 1,
                "nestedModel": {
                    "intValue": 2,
                    "strValue": "3",
                    "authorizationList": [
                        {
                            "chainId": 22,
                            "address": "0x" + "00" * 19 + "01",
                            "nonce": 1999,
                            "yParity": 1,
                            "r": 123456789,
                            "s": 987654321,
                        }
                    ],
                },
            },
        ),
    ),
)
def test_pydantic_model_serialization(pydantic_model, expected):
    json_model_dump = pydantic_model.model_dump(by_alias=True)
    with pytest.warns(DeprecationWarning):
        recursive_dump = pydantic_model.recursive_model_dump()
    assert json_model_dump == recursive_dump == expected
    assert json.loads(json.dumps(recursive_dump)) == expected

    model_dump = pydantic_model.model_dump()
    snake_case_dump = pydantic_model.model_dump(by_alias=False)
    assert snake_case_dump == model_dump != expected

    camel_keys = {to_camel(key) for key in model_dump.keys()}
    assert set(camel_keys).issubset(set(expected.keys()))


@pytest.mark.parametrize(
    "pydantic_model", (TEST_SIGNED_AUTHORIZATION, PydanticTestClass())
)
def test_pydantic_model_json_schema(pydantic_model):
    schema = pydantic_model.model_json_schema(by_alias=True)
    assert isinstance(schema, dict)
