import pytest

from eth_account._utils.encode_typed_data import (
    _get_primary_type,
    encode_data,
    encode_field,
    encode_type,
    find_type_dependencies,
    hash_domain,
    hash_struct,
    hash_type,
)


@pytest.mark.parametrize(
    "types, expected",
    (
        (
            {
                "Person": [
                    {"name": "name", "type": "string"},
                ],
            },
            "Person",
        ),
        (
            {
                "Person": [
                    {"name": "name", "type": "string"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                ],
            },
            "Mail",
        ),
        (
            {
                "Person": [
                    {"name": "name", "type": "string"},
                    {"name": "friend", "type": "Person"},
                ],
            },
            "Person",
        ),
        (
            {
                "Person": [
                    {"name": "name", "type": "string"},
                    {"name": "friends", "type": "Person[]"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                    {"name": "attachments", "type": "Attachment[]"},
                ],
                "Attachment": [
                    {"name": "from", "type": "string"},
                ],
            },
            "Mail",
        ),
    ),
    ids=[
        "primary_type with no dependencies",
        "primary_type with one dependency",
        "primary_type with recursive dependency",
        "primary_type with array dependency",
    ],
)
def test_get_primary_type_pass(types, expected):
    assert _get_primary_type(types) == expected


@pytest.mark.parametrize(
    "types, expected",
    (
        (
            {
                "Person": [
                    {"name": "other_person", "type": "OtherPerson"},
                ],
                "OtherPerson": [
                    {"name": "Person", "type": "Person"},
                ],
            },
            {
                "expected_exception": ValueError,
                "match": "Unable to determine primary type",
            },
        ),
        (
            {
                "Person": [
                    {"name": "name", "type": "string"},
                ],
                "Mail": [
                    {"name": "type", "type": "string"},
                ],
            },
            {
                "expected_exception": ValueError,
                "match": "Unable to determine primary type",
            },
        ),
    ),
    ids=[
        "primary_type circular dependency",
        "two primary types that do not depend on each other",
    ],
)
def test_get_primary_type_fail(types, expected):
    with pytest.raises(**expected):
        _get_primary_type(types)


@pytest.mark.parametrize(
    "name, type_, value, expected",
    (
        (
            "custom_type",
            "Sample",
            None,
            (
                "bytes32",
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",  # noqa: E501
            ),
        ),
        (
            "name",
            "string",
            None,
            (
                "bytes32",
                b"",
            ),
        ),
        (
            "some_bytes",
            "bytes",
            None,
            (
                "bytes32",
                b"",
            ),
        ),
        (
            "some_bytes",
            "bytes",
            27,
            (
                "bytes32",
                b"$\xd6\xd74\x14_\x07\x1a\xa6\xa2v?\xdd\xcaX\x10\xbd\x12#l->X\x9d*z\xdf\\\xa6\x9c\xc9\xc6",  # noqa: E501
            ),
        ),
        (
            "some_bytes",
            "bytes",
            "0xdeadbeef",
            (
                "bytes32",
                b"\xd4\xfdN\x18\x912'06D\x9f\xc9\xe1\x11\x98\xc79\x16\x1bL\x01\x16\xa9\xa2\xdc\xcd\xfa\x1cI \x06\xf1",  # noqa: E501
            ),
        ),
        (
            "some_bytes",
            "bytes",
            b"\xd4\xfdN\x18\x912'06D\x9f\xc9\xe1\x11",
            (
                "bytes32",
                b"p\xa6\xe6 \xc0:\xff\xea9\x0f\xad\x1a\xab\xf8\xf7\xdc\x1b\xd1\x82\x1c\xe4\xd5\xa1,m3+\x15X\x98M\xaf",  # noqa: E501
            ),
        ),
        (
            "name",
            "string",
            27,
            (
                "bytes32",
                b"$\xd6\xd74\x14_\x07\x1a\xa6\xa2v?\xdd\xcaX\x10\xbd\x12#l->X\x9d*z\xdf\\\xa6\x9c\xc9\xc6",  # noqa: E501
            ),
        ),
        (
            "name",
            "string",
            "Bob",
            (
                "bytes32",
                b"(\xca\xc3\x18\xa8l\x8a\nj\x91V\xc2\xdb\xa2\xc8\xc266w\xba\x05\x14\xefae\x92\xd8\x15W\xe6y\xb6",  # noqa: E501
            ),
        ),
        (
            "names",
            "string[]",
            "['Bob', 'Jim']",
            (
                "bytes32",
                b"\xd3\xd6\xa8?%\x9eN{\xe2\xffP\xa5\xb3\xac\xa7.i\xa6\x92^\x0eq\x8c,\x12[\xeaR\xb1\xc6\x19\x1b",  # noqa: E501
            ),
        ),
        (
            "names",
            "string[][]",
            "[['Bob', 'Jim'],['Amy', 'Sal']]",
            (
                "bytes32",
                b"$\\\x93)\x01\x91\x1a\xd7Z\x0f\x12\xd9\x93\xe6\xd9\xb1\x02\xb2\xfe\xf1\x97\xaa\xd7\x8a\xf6p\xe1\x7f\xc7\xe9v\x83",  # noqa: E501
            ),
        ),
        (
            "a_bool",
            "bool",
            True,
            (
                "bool",
                True,
            ),
        ),
        (
            "an_address",
            "address",
            "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC",
            (
                "address",
                "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC",
            ),
        ),
        (
            "an_int16",
            "int16",
            -25,
            (
                "int16",
                -25,
            ),
        ),
        (
            "a_uint256",
            "uint256",
            1157920892373161954235709850086879078532699846656,
            (
                "uint256",
                1157920892373161954235709850086879078532699846656,
            ),
        ),
        (
            "empty_string",
            "string",
            "",
            (
                "bytes32",
                b"\xc5\xd2F\x01\x86\xf7#<\x92~}\xb2\xdc\xc7\x03\xc0\xe5\x00\xb6S\xca\x82';{\xfa\xd8\x04]\x85\xa4p",  # noqa: E501
            ),
        ),
        (
            "expected_sample",
            "Sample",
            {
                "name": "Cow",
            },
            (
                "bytes32",
                b"\x8flivK`W\xf4my$tFGG\x9f\x99k\xbe\xb9\x8e\xcfh]\xcb\x8b\x8ak\xb9\xe5\x17\xdd",  # noqa: E501
            ),
        ),
        (
            "expected_samples",
            "Samples",
            {
                "samples": [
                    {
                        "name": "Abe",
                    },
                    {
                        "name": "Bob",
                    },
                    {
                        "name": "Cow",
                    },
                ],
            },
            (
                "bytes32",
                b"\x94}\xef\x19'\xda\xc4\x1f\x85\xfb\x87ya\x8e\x1f\x87\x96L(\x80\\\xeb\t\xe6Gv8\x0c\x19k\\\t",  # noqa: E501
            ),
        ),
    ),
    ids=[
        "None value for custom type",
        "None value for string type",
        "None value for bytes type",
        "int value for bytes type",
        "hexstr value for bytes type",
        "bytes value for bytes type",
        "int value for string type",
        "string value for string type",
        "string[] value for string[] type",
        "string[][] value for string[][] type",
        "bool value for bool type",
        "address value for address type",
        "int16 value for int16 type",
        "uint256 value for uint256 type",
        "empty string value for string type",
        "expected value for custom type",
        "expected value for custom type array",
    ],
)
def test_encode_field_pass(name, type_, value, expected):
    types = {
        "Sample": [
            {"name": "name", "type": "string"},
        ],
        "Samples": [
            {"name": "samples", "type": "Sample[]"},
        ],
    }
    assert encode_field(types, name, type_, value) == expected


@pytest.mark.parametrize(
    "name, type_, value, expected",
    (
        (
            "atomic_type",
            "address",
            None,
            {
                "expected_exception": ValueError,
                "match": "missing value for field atomic_type of type address",
            },
        ),
    ),
    ids=[
        "None value for atomic type",
    ],
)
def test_encode_field_fail(name, type_, value, expected):
    types = {
        "Sample": [
            {"name": "name", "type": "string"},
        ]
    }

    with pytest.raises(**expected):
        encode_field(types, name, type_, value)


@pytest.mark.parametrize(
    "primary_type, types, expected",
    (
        (
            "Person",
            {
                "Person": [
                    {"name": "name", "type": "string"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                ],
            },
            {"Person"},
        ),
        (
            "Mail",
            {
                "Person": [
                    {"name": "name", "type": "string"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                ],
            },
            {"Person", "Mail"},
        ),
        (
            "Person",
            {
                "Person": [
                    {"name": "name", "type": "string"},
                    {"name": "friend", "type": "Person"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                ],
            },
            {"Person"},
        ),
        (
            "Mail",
            {
                "Person": [
                    {"name": "name", "type": "string"},
                    {"name": "friends", "type": "Person[]"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                    {"name": "attachments", "type": "Attachment[]"},
                ],
                "Attachment": [
                    {"name": "from", "type": "string"},
                ],
            },
            {"Person", "Mail", "Attachment"},
        ),
        (
            "Ma il!",
            {
                "Person": [
                    {"name": "name", "type": "string"},
                    {"name": "friends", "type": "Person"},
                ],
                "Ma il!": [
                    {"name": "from", "type": "Person"},
                    {"name": "attachments", "type": "Attachment[]"},
                ],
                "Attachment": [
                    {"name": "from", "type": "string"},
                ],
            },
            {"Person", "Ma il!", "Attachment"},
        ),
    ),
    ids=[
        "type with no dependencies",
        "type with one dependency",
        "type with recursive dependency",
        "type with array dependency",
        "type with non-alphanumeric in primary type",
    ],
)
def test_find_type_dependencies_pass(primary_type, types, expected):
    assert find_type_dependencies(primary_type, types) == expected


@pytest.mark.parametrize(
    "primary_type, types, expected",
    (
        (
            27,
            {
                27: [
                    {"name": "name", "type": "string"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                ],
            },
            {
                "expected_exception": ValueError,
                "match": "Invalid find_type_dependencies input: expected string, "
                "got 27 of type <class 'int'>",
            },
        ),
        (
            "Person",
            {
                "Person": [
                    {"name": "name", "type": "string"},
                    {"name": "pet", "type": "Animal"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                ],
            },
            {
                "expected_exception": ValueError,
                "match": "No definition of type Animal",
            },
        ),
        (
            "Mail",
            {
                "Person": [
                    {"name": "name", "type": "string"},
                    {"name": "friends", "type": "Person[]"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                    {"name": "attachments", "type": "Attachment[]"},
                ],
            },
            {
                "expected_exception": ValueError,
                "match": "No definition of type Attachment",
            },
        ),
    ),
    ids=[
        "primary_type must be a string",
        "custom type in dependencies but not defined in types",
        "custom type array in dependencies but not defined in types",
    ],
)
def test_find_type_dependencies_fail(primary_type, types, expected):
    with pytest.raises(**expected):
        find_type_dependencies(primary_type, types)


@pytest.mark.parametrize(
    "primary_type, types, encode_type_expected, hash_type_expected",
    (
        (
            "Person",
            {
                "Person": [
                    {"name": "name", "type": "string"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                ],
            },
            "Person(string name)",
            "fcbb73369ebb221abfdc626fdec0be9ca48ad89ef757b9a76eb7b31ddd261338",
        ),
        (
            "Mail",
            {
                "Person": [
                    {"name": "name", "type": "string"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                ],
            },
            "Mail(Person from)Person(string name)",
            "979fb836e7a3c69210ec4cfec014139732f26442be0f5c10c4222ccabfe6a025",
        ),
        (
            "Person",
            {
                "Person": [
                    {"name": "name", "type": "string"},
                    {"name": "friend", "type": "Person"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                ],
            },
            "Person(string name,Person friend)",
            "945f8587e8daf26c14c625b054bfccb52dc48747984b7925c0901efca7186e14",
        ),
        (
            "Mail",
            {
                "Person": [
                    {"name": "name", "type": "string"},
                    {"name": "friends", "type": "Person[]"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                    {"name": "attachments", "type": "Attachment[]"},
                ],
                "Attachment": [
                    {"name": "from", "type": "string"},
                ],
            },
            "Mail(Person from,Attachment[] attachments)Attachment(string from)Person(string name,Person[] friends)",  # noqa: E501
            "0c555dd4d869769a9f68c39860155342ea7e75a215669bc44efca1b4544735e5",
        ),
        (
            "Ma il!",
            {
                "Person": [
                    {"name": "name", "type": "string"},
                    {"name": "friends", "type": "Person"},
                ],
                "Ma il!": [
                    {"name": "from", "type": "Person"},
                    {"name": "attachments", "type": "Attachment[]"},
                ],
                "Attachment": [
                    {"name": "from", "type": "string"},
                ],
            },
            "Ma il!(Person from,Attachment[] attachments)Attachment(string from)Person(string name,Person friends)",  # noqa: E501
            "099b05cabe783f37d88d94e349693aca4fc9ae40c51e5d2640ff040768e5b2ad",
        ),
    ),
    ids=[
        "type with no dependencies",
        "type with one dependency",
        "type with recursive dependency",
        "type with array dependency",
        "type with non-alphanumeric in primary type",
    ],
)
def test_encode_type_pass_and_hash_type(
    primary_type, types, encode_type_expected, hash_type_expected
):
    assert encode_type(primary_type, types) == encode_type_expected
    assert hash_type(primary_type, types).hex() == hash_type_expected


@pytest.mark.parametrize(
    "primary_type, types, expected",
    (
        (
            "Mail",
            {
                "Person": [
                    {"name": "name", "type": "string"},
                    {"name": "friends", "type": "Person[]"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                    {"name": "attachments", "type": "Attachment[]"},
                ],
            },
            {
                "expected_exception": ValueError,
                "match": "No definition of type Attachment",
            },
        ),
    ),
    ids=[
        "custom type array in dependencies but not defined in types",
    ],
)
def test_encode_type_fail(primary_type, types, expected):
    with pytest.raises(**expected):
        encode_type(primary_type, types)


@pytest.mark.parametrize(
    "type_, message, types, encode_data_expected, hash_struct_expected",
    (
        (
            "Mail",
            {
                "from": {
                    "name": "Cow",
                },
            },
            {
                "Person": [
                    {"name": "name", "type": "string"},
                ],
                "Mail": [
                    {"name": "from", "type": "Person"},
                ],
            },
            "979fb836e7a3c69210ec4cfec014139732f26442be0f5c10c4222ccabfe6a025bfb54ec5e6bf391ea339a110356cb0fd003296b0dabe4b0b2e51d0e50c815c8a",  # noqa: E501
            "dfa5fd27fea278587b6c6a56d8e6cf2853b6698a4244afc1f5f526f04b2b70b3",
        ),
        # (
        #     "Person",
        #     {
        #         "Person": [
        #             {"name": "name", "type": "string"},
        #         ],
        #         "Mail": [
        #             {"name": "from", "type": "Person"},
        #         ],
        #     },
        #     "Person(string name)",
        # ),
        # (
        #     "Mail",
        #     {
        #         "Person": [
        #             {"name": "name", "type": "string"},
        #         ],
        #         "Mail": [
        #             {"name": "from", "type": "Person"},
        #         ],
        #     },
        #     "Mail(Person from)Person(string name)",
        # ),
        # (
        #     "Person",
        #     {
        #         "Person": [
        #             {"name": "name", "type": "string"},
        #             {"name": "friend", "type": "Person"},
        #         ],
        #         "Mail": [
        #             {"name": "from", "type": "Person"},
        #         ],
        #     },
        #     "Person(string name,Person friend)",
        # ),
        # (
        #     "Mail",
        #     {
        #         "Person": [
        #             {"name": "name", "type": "string"},
        #             {"name": "friends", "type": "Person[]"},
        #         ],
        #         "Mail": [
        #             {"name": "from", "type": "Person"},
        #             {"name": "attachments", "type": "Attachment[]"},
        #         ],
        #         "Attachment": [
        #             {"name": "from", "type": "string"},
        #         ],
        #     },
        #     "Mail(Person from,Attachment[] attachments)Attachment(string from)Person(string name,Person[] friends)",  # noqa: E501
        # ),
        # (
        #     "Ma il!",
        #     {
        #         "Person": [
        #             {"name": "name", "type": "string"},
        #             {"name": "friends", "type": "Person"},
        #         ],
        #         "Ma il!": [
        #             {"name": "from", "type": "Person"},
        #             {"name": "attachments", "type": "Attachment[]"},
        #         ],
        #         "Attachment": [
        #             {"name": "from", "type": "string"},
        #         ],
        #     },
        #     "Ma il!(Person from,Attachment[] attachments)Attachment(string from)Person(string name,Person friends)",  # noqa: E501
        # ),
    ),
    ids=[
        "primary type with one custom type dependency",
        # "type with no dependencies",
        # "type with one dependency",
        # "type with recursive dependency",
        # "type with array dependency",
        # "type with non-alphanumeric in primary type",
    ],
)
def test_encode_data_pass_and_hash_struct(
    type_, message, types, encode_data_expected, hash_struct_expected
):
    assert encode_data(type_, types, message).hex() == encode_data_expected
    assert hash_struct(type_, types, message).hex() == hash_struct_expected


@pytest.mark.parametrize(
    "domain_data, expected",
    (
        (
            {
                "name": "Ether Mail",
                "version": "1",
                "chainId": 1,
                "verifyingContract": "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC",
            },
            "f2cee375fa42b42143804025fc449deafd50cc031ca257e0b194a650a912090f",
        ),
        (
            {},
            "6192106f129ce05c9075d319c1fa6ea9b3ae37cbd0c1ef92e2be7137bb07baa1",
        ),
    ),
    ids=[
        "EIP712 example domain data",
        "empty domain data",
    ],
)
def test_hash_domain_pass(domain_data, expected):
    assert hash_domain(domain_data).hex() == expected


@pytest.mark.parametrize(
    "domain_data, expected",
    (
        (
            {
                "name": "Ether Mail",
                "classification": "1",
                "chainId": 1,
                "verifyingContract": "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC",
            },
            {
                "expected_exception": ValueError,
                "match": "Invalid domain key: classification",
            },
        ),
    ),
    ids=[
        "key in domain_data not in EIP712 domain fields",
    ],
)
def test_hash_domain_fail(domain_data, expected):
    with pytest.raises(**expected):
        hash_domain(domain_data)
