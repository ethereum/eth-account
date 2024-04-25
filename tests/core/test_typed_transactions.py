import pytest

from hexbytes import (
    HexBytes,
)

from eth_account.typed_transactions import (
    AccessListTransaction,
    BlobTransaction,
    DynamicFeeTransaction,
    TypedTransaction,
)

TEST_CASES = [
    {
        "expected_type": AccessListTransaction,
        "expected_hash": "0x4f53cc08773081c51a1da2dc8df07b2e58cf8e359239efdb8dbf049be448974d",  # noqa: E501
        "expected_raw_transaction": "0x01f8ad82076c22843b9aca00830186a09409616c3d61b3331fc4109a9e41a8bdb7d9776609865af3107a400086616263646566f838f7940000000000000000000000000000000000000001e1a0010000000000000000000000000000000000000000000000000000000000000001a08289e85fa00f8f7f78a53cf147a87b2a7f0d27e64d7571f9d06a802e365c3430a017dc77eae36c88937db4a5179f57edc6119701652f3f1c6f194d1210d638a061",  # noqa: 501
        "transaction": {
            "gas": "0x186a0",
            "gasPrice": "0x3b9aca00",
            "data": "0x616263646566",
            "nonce": "0x22",
            "to": "0x09616C3d61b3331fc4109a9E41a8BDB7d9776609",
            "value": "0x5af3107a4000",
            "type": "0x1",
            "accessList": (
                {
                    "address": "0x0000000000000000000000000000000000000001",
                    "storageKeys": (
                        "0x0100000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                    ),
                },
            ),
            "chainId": "0x76c",
            "v": "0x1",
            "r": "0x8289e85fa00f8f7f78a53cf147a87b2a7f0d27e64d7571f9d06a802e365c3430",
            "s": "0x17dc77eae36c88937db4a5179f57edc6119701652f3f1c6f194d1210d638a061",
        },
    },
    {
        "expected_type": AccessListTransaction,
        "expected_hash": "0x660fd2280b7ce4a6b625ccb2e1bb56fe3ede2ed91a7ff0b82a8d61e4709b82f6",  # noqa: E501
        "expected_raw_transaction": "0x01f87482076c27843b9aca00830186a09409616c3d61b3331fc4109a9e41a8bdb7d9776609865af3107a400086616263646566c080a0bad1a40fa2d90dc7539831bb82dfccf9b7094eab238d50c4369b805fb7241c58a046ab7eb7ff8cdfd203847b7e1b2f9e41208bba76a86ae3eeb97fe2727763aa12",  # noqa: 501
        "transaction": {
            "gas": "0x186a0",
            "gasPrice": "0x3b9aca00",
            "data": "0x616263646566",
            "nonce": "0x27",
            "to": "0x09616C3d61b3331fc4109a9E41a8BDB7d9776609",
            "value": "0x5af3107a4000",
            "type": "0x1",
            "accessList": (),
            "chainId": "0x76c",
            "v": "0x0",
            "r": "0xbad1a40fa2d90dc7539831bb82dfccf9b7094eab238d50c4369b805fb7241c58",
            "s": "0x46ab7eb7ff8cdfd203847b7e1b2f9e41208bba76a86ae3eeb97fe2727763aa12",
        },
    },
    {
        "expected_type": AccessListTransaction,
        "expected_hash": "0x99d4267647b68de80da39423b78e060989d89d2d128c94621525999dc05dfab9",  # noqa: E501
        "expected_raw_transaction": "0x01f9022882053912843b9aca00830186a09496216849c49358b10257cb55b28ea603c874b05e865af3107a4000825544f901b6f8dd94290a6a7460b308ee3f19023d2d00de604bcf5b42f8c6a00000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000001a00000000000000000000000000000000000000000000000000000000000000004a0b4c32d61ed12936769c68071a161309a6848a0d43ffce43d5f529f86b73529c3a0b4c32d61ed12936769c68071a161309a6848a0d43ffce43d5f529f86b73529c4a0b4c32d61ed12936769c68071a161309a6848a0d43ffce43d5f529f86b73529c5f87a947d1afa7b718fb893db30a3abc0cfc608aacfebb0f863a014d5312942240e565c56aec11806ce58e3c0e38c96269d759c5d35a2a2e4a449a037b0b82ee5d8a88672df3895a46af48bbcd30d6efcc908136e29456fa30604bba0bc3269c3ddeb063124d8c8f40c383f40b2d3212d819cd058041d83e583892d9af85994c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2f842a02c47f2c83db5d085fba21d1d91bba6245435c688f64423ba360424c27e4558f2a08275c17064fd92fe5b41f3fc855dd1c473a6b1800a19406cb089c51a5c17536180a04c543fe5721a5633cf50a3aeaef767825aa4f6259bfe157995c2ebf588f6c0b9a0269ea7a6257dc14fec5bb2cd94e7bc4a5640799aa5d9becedac4d3e9ec443d06",  # noqa: 501
        "transaction": {
            "gas": "0x186a0",
            "gasPrice": "0x3b9aca00",
            "data": "0x5544",
            "nonce": "0x12",
            "to": "0x96216849c49358B10257cb55b28eA603c874b05E",
            "value": "0x5af3107a4000",
            "type": "0x1",
            "accessList": (
                {
                    "address": "0x290a6a7460b308ee3f19023d2d00de604bcf5b42",
                    "storageKeys": (
                        "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                        "0x0000000000000000000000000000000000000000000000000000000000000001",  # noqa: E501
                        "0x0000000000000000000000000000000000000000000000000000000000000004",  # noqa: E501
                        "0xb4c32d61ed12936769c68071a161309a6848a0d43ffce43d5f529f86b73529c3",  # noqa: E501
                        "0xb4c32d61ed12936769c68071a161309a6848a0d43ffce43d5f529f86b73529c4",  # noqa: E501
                        "0xb4c32d61ed12936769c68071a161309a6848a0d43ffce43d5f529f86b73529c5",  # noqa: E501
                    ),
                },
                {
                    "address": "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0",
                    "storageKeys": (
                        "0x14d5312942240e565c56aec11806ce58e3c0e38c96269d759c5d35a2a2e4a449",  # noqa: E501
                        "0x37b0b82ee5d8a88672df3895a46af48bbcd30d6efcc908136e29456fa30604bb",  # noqa: E501
                        "0xbc3269c3ddeb063124d8c8f40c383f40b2d3212d819cd058041d83e583892d9a",  # noqa: E501
                    ),
                },
                {
                    "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                    "storageKeys": (
                        "0x2c47f2c83db5d085fba21d1d91bba6245435c688f64423ba360424c27e4558f2",  # noqa: E501
                        "0x8275c17064fd92fe5b41f3fc855dd1c473a6b1800a19406cb089c51a5c175361",  # noqa: E501
                    ),
                },
            ),
            "chainId": "0x539",
            "v": "0x0",
            "r": "0x4c543fe5721a5633cf50a3aeaef767825aa4f6259bfe157995c2ebf588f6c0b9",
            "s": "0x269ea7a6257dc14fec5bb2cd94e7bc4a5640799aa5d9becedac4d3e9ec443d06",
        },
    },
    {
        "expected_type": AccessListTransaction,
        "expected_hash": "0x99d4267647b68de80da39423b78e060989d89d2d128c94621525999dc05dfab9",  # noqa: E501
        "expected_raw_transaction": "0x01f9022882053912843b9aca00830186a09496216849c49358b10257cb55b28ea603c874b05e865af3107a4000825544f901b6f8dd94290a6a7460b308ee3f19023d2d00de604bcf5b42f8c6a00000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000001a00000000000000000000000000000000000000000000000000000000000000004a0b4c32d61ed12936769c68071a161309a6848a0d43ffce43d5f529f86b73529c3a0b4c32d61ed12936769c68071a161309a6848a0d43ffce43d5f529f86b73529c4a0b4c32d61ed12936769c68071a161309a6848a0d43ffce43d5f529f86b73529c5f87a947d1afa7b718fb893db30a3abc0cfc608aacfebb0f863a014d5312942240e565c56aec11806ce58e3c0e38c96269d759c5d35a2a2e4a449a037b0b82ee5d8a88672df3895a46af48bbcd30d6efcc908136e29456fa30604bba0bc3269c3ddeb063124d8c8f40c383f40b2d3212d819cd058041d83e583892d9af85994c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2f842a02c47f2c83db5d085fba21d1d91bba6245435c688f64423ba360424c27e4558f2a08275c17064fd92fe5b41f3fc855dd1c473a6b1800a19406cb089c51a5c17536180a04c543fe5721a5633cf50a3aeaef767825aa4f6259bfe157995c2ebf588f6c0b9a0269ea7a6257dc14fec5bb2cd94e7bc4a5640799aa5d9becedac4d3e9ec443d06",  # noqa: 501
        "transaction": {
            "gas": "0x186a0",
            "gasPrice": "0x3b9aca00",
            "data": "0x5544",
            "nonce": "0x12",
            "to": "0x96216849c49358B10257cb55b28eA603c874b05E",
            "value": "0x5af3107a4000",
            "type": "0x1",
            "accessList": [
                {
                    "address": "0x290a6a7460b308ee3f19023d2d00de604bcf5b42",
                    "storageKeys": [
                        "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                        "0x0000000000000000000000000000000000000000000000000000000000000001",  # noqa: E501
                        "0x0000000000000000000000000000000000000000000000000000000000000004",  # noqa: E501
                        "0xb4c32d61ed12936769c68071a161309a6848a0d43ffce43d5f529f86b73529c3",  # noqa: E501
                        "0xb4c32d61ed12936769c68071a161309a6848a0d43ffce43d5f529f86b73529c4",  # noqa: E501
                        "0xb4c32d61ed12936769c68071a161309a6848a0d43ffce43d5f529f86b73529c5",  # noqa: E501
                    ],
                },
                {
                    "address": "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0",
                    "storageKeys": [
                        "0x14d5312942240e565c56aec11806ce58e3c0e38c96269d759c5d35a2a2e4a449",  # noqa: E501
                        "0x37b0b82ee5d8a88672df3895a46af48bbcd30d6efcc908136e29456fa30604bb",  # noqa: E501
                        "0xbc3269c3ddeb063124d8c8f40c383f40b2d3212d819cd058041d83e583892d9a",  # noqa: E501
                    ],
                },
                {
                    "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                    "storageKeys": [
                        "0x2c47f2c83db5d085fba21d1d91bba6245435c688f64423ba360424c27e4558f2",  # noqa: E501
                        "0x8275c17064fd92fe5b41f3fc855dd1c473a6b1800a19406cb089c51a5c175361",  # noqa: E501
                    ],
                },
            ],
            "chainId": "0x539",
            "v": "0x0",
            "r": "0x4c543fe5721a5633cf50a3aeaef767825aa4f6259bfe157995c2ebf588f6c0b9",
            "s": "0x269ea7a6257dc14fec5bb2cd94e7bc4a5640799aa5d9becedac4d3e9ec443d06",
        },
    },
    {
        "expected_type": AccessListTransaction,
        "expected_hash": "0x8d46e14b6259a070e0c4a7be7ed73bb18838cfb022b9c381e426cf7b3e22ec12",  # noqa: E501
        "expected_raw_transaction": "0x01f8e782076c22843b9aca00830186a09409616c3d61b3331fc4109a9e41a8bdb7d9776609865af3107a400086616263646566f872f85994de0b295669a9fd93d5f28d9ec85e40f4cb697baef842a00000000000000000000000000000000000000000000000000000000000000003a00000000000000000000000000000000000000000000000000000000000000007d694bb9bc244d798123fde783fcc1c72d3bb8c189413c001a08289e85fa00f8f7f78a53cf147a87b2a7f0d27e64d7571f9d06a802e365c3430a017dc77eae36c88937db4a5179f57edc6119701652f3f1c6f194d1210d638a061",  # noqa: 501
        "transaction": {
            "gas": "0x186a0",
            "gasPrice": "0x3b9aca00",
            "data": "0x616263646566",
            "nonce": "0x22",
            "to": "0x09616C3d61b3331fc4109a9E41a8BDB7d9776609",
            "value": "0x5af3107a4000",
            "accessList": (  # test case from EIP-2930
                {
                    "address": "0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae",
                    "storageKeys": (
                        "0x0000000000000000000000000000000000000000000000000000000000000003",  # noqa: E501
                        "0x0000000000000000000000000000000000000000000000000000000000000007",  # noqa: E501
                    ),
                },
                {
                    "address": "0xbb9bc244d798123fde783fcc1c72d3bb8c189413",
                    "storageKeys": (),
                },
            ),
            "chainId": "0x76c",
            "v": "0x1",
            "r": "0x8289e85fa00f8f7f78a53cf147a87b2a7f0d27e64d7571f9d06a802e365c3430",
            "s": "0x17dc77eae36c88937db4a5179f57edc6119701652f3f1c6f194d1210d638a061",
        },
    },
    {
        "expected_type": DynamicFeeTransaction,
        "expected_hash": "0xa1ea3121940930f7e7b54506d80717f14c5163807951624c36354202a8bffda6",  # noqa: E501
        "expected_raw_transaction": "0x02f8758205390284773594008477359400830186a09496216849c49358b10257cb55b28ea603c874b05e865af3107a4000825544c001a0c3000cd391f991169ebfd5d3b9e93c89d31a61c998a21b07a11dc6b9d66f8a8ea022cfe8424b2fbd78b16c9911da1be2349027b0a3c40adf4b6459222323773f74",  # noqa: 501
        "transaction": {
            "gas": "0x186a0",
            "maxFeePerGas": "0x77359400",
            "maxPriorityFeePerGas": "0x77359400",
            "data": "0x5544",
            "nonce": "0x2",
            "to": "0x96216849c49358B10257cb55b28eA603c874b05E",
            "value": "0x5af3107a4000",
            "type": "0x2",
            "chainId": "0x539",
            "accessList": (),
            "v": "0x1",
            "r": "0xc3000cd391f991169ebfd5d3b9e93c89d31a61c998a21b07a11dc6b9d66f8a8e",
            "s": "0x22cfe8424b2fbd78b16c9911da1be2349027b0a3c40adf4b6459222323773f74",
        },
    },
    {
        "expected_type": DynamicFeeTransaction,
        "expected_hash": "0x090b19818d9d087a49c3d2ecee4829ee4acea46089c1381ac5e588188627466d",  # noqa: E501
        "expected_raw_transaction": "0x02f8ae8205390284773594008477359400830186a09496216849c49358b10257cb55b28ea603c874b05e865af3107a4000825544f838f7940000000000000000000000000000000000000001e1a0010000000000000000000000000000000000000000000000000000000000000001a0c3000cd391f991169ebfd5d3b9e93c89d31a61c998a21b07a11dc6b9d66f8a8ea022cfe8424b2fbd78b16c9911da1be2349027b0a3c40adf4b6459222323773f74",  # noqa: 501
        "transaction": {
            "gas": 100000,
            "maxFeePerGas": 2000000000,
            "maxPriorityFeePerGas": 2000000000,
            "data": "0x5544",
            "nonce": 2,
            "to": "0x96216849c49358B10257cb55b28eA603c874b05E",
            "value": 100000000000000,
            "type": 2,
            "accessList": [
                {
                    "address": "0x0000000000000000000000000000000000000001",
                    "storageKeys": (
                        "0x0100000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                    ),
                },
            ],
            "chainId": 1337,
            "v": "0x1",
            "r": "0xc3000cd391f991169ebfd5d3b9e93c89d31a61c998a21b07a11dc6b9d66f8a8e",
            "s": "0x22cfe8424b2fbd78b16c9911da1be2349027b0a3c40adf4b6459222323773f74",
        },
    },
    {
        "expected_type": DynamicFeeTransaction,
        "expected_hash": "0x090b19818d9d087a49c3d2ecee4829ee4acea46089c1381ac5e588188627466d",  # noqa: E501
        "expected_raw_transaction": "0x02f8ae8205390284773594008477359400830186a09496216849c49358b10257cb55b28ea603c874b05e865af3107a4000825544f838f7940000000000000000000000000000000000000001e1a0010000000000000000000000000000000000000000000000000000000000000001a0c3000cd391f991169ebfd5d3b9e93c89d31a61c998a21b07a11dc6b9d66f8a8ea022cfe8424b2fbd78b16c9911da1be2349027b0a3c40adf4b6459222323773f74",  # noqa: 501
        "transaction": {
            "gas": 100000,
            "maxFeePerGas": 2000000000,
            "maxPriorityFeePerGas": 2000000000,
            "data": "0x5544",
            "nonce": "0x2",
            "to": "0x96216849c49358B10257cb55b28eA603c874b05E",
            "value": "0x5af3107a4000",
            "accessList": (
                {
                    "address": "0x0000000000000000000000000000000000000001",
                    "storageKeys": (
                        "0x0100000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                    ),
                },
            ),
            "chainId": "0x539",
            "v": "0x1",
            "r": "0xc3000cd391f991169ebfd5d3b9e93c89d31a61c998a21b07a11dc6b9d66f8a8e",
            "s": "0x22cfe8424b2fbd78b16c9911da1be2349027b0a3c40adf4b6459222323773f74",
        },
    },
    {
        "expected_type": BlobTransaction,
        "expected_hash": "0xdc5c66152fa69fc4f43aa0712104e9a9c9559dcc40d66d3fe3bed84daf8305b8",  # noqa: E501
        "expected_raw_transaction": "0x03f89c8205390284773594008477359400830186a09496216849c49358b10257cb55b28ea603c874b05e865af3107a4000825544c08477359400e1a001a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d801a0be1552b754ad4aeb9fef74bbe1adc9384e2e78f873480e510b932847cdae9a58a03a4cfa2158d6a9d4d54ff42eedbedfdad0573366cb757209179107b15b1a1eeb",  # noqa: 501
        "transaction": {
            "gas": 100000,
            "maxFeePerGas": 2000000000,
            "maxPriorityFeePerGas": 2000000000,
            "maxFeePerBlobGas": 2000000000,
            "blobVersionedHashes": [
                "0x01a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8"
            ],
            "data": "0x5544",
            "nonce": 2,
            "to": "0x96216849c49358B10257cb55b28eA603c874b05E",
            "value": 100000000000000,
            "type": 3,
            "chainId": 1337,
            "accessList": [],
            "v": "0x1",
            "r": "0xbe1552b754ad4aeb9fef74bbe1adc9384e2e78f873480e510b932847cdae9a58",
            "s": "0x3a4cfa2158d6a9d4d54ff42eedbedfdad0573366cb757209179107b15b1a1eeb",
        },
    },
    {
        "expected_type": BlobTransaction,
        "expected_hash": "0x5fb3359709f5b7b14d10f05948e38d35e12efd626e733b200cb4742f52fc65a3",  # noqa: E501
        "expected_raw_transaction": "0x03f8ec820539800285012a05f200833d090094095e7baea6a6c7c4c2dfeb977efac326af552d87830186a000f85bf85994095e7baea6a6c7c4c2dfeb977efac326af552d87f842a00000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000010ae1a001a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d801a0d10cbee5653bdc5c2b0bafe8a88efafc6d9f5123815178783a4d7820937917faa03040e5f117d33a7873d8bfa8fad8bf5d1163db2ce4e3de5ea414a45e199b5b2d",  # noqa: E501
        "transaction": {
            "accessList": (
                {
                    "address": "0x095E7BAea6a6c7c4c2DfeB977eFac326aF552d87",
                    "storageKeys": (
                        "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                        "0x0000000000000000000000000000000000000000000000000000000000000001",  # noqa: E501
                    ),
                },
            ),
            "blobVersionedHashes": [
                "0x01a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8"
            ],
            "data": "0x00",
            "gas": "0x3d0900",
            "maxFeePerBlobGas": "0x0a",
            "maxFeePerGas": "0x012a05f200",
            "maxPriorityFeePerGas": "0x02",
            "nonce": "0x00",
            "to": "0x095E7BAea6a6c7c4c2DfeB977eFac326aF552d87",
            "value": "0x0186a0",
            "chainId": "0x539",
            "type": "0x3",
            "v": "0x1",
            "r": "0xd10cbee5653bdc5c2b0bafe8a88efafc6d9f5123815178783a4d7820937917fa",
            "s": "0x3040e5f117d33a7873d8bfa8fad8bf5d1163db2ce4e3de5ea414a45e199b5b2d",
        },
    },
    {
        "expected_type": BlobTransaction,
        "expected_hash": "0x5fb3359709f5b7b14d10f05948e38d35e12efd626e733b200cb4742f52fc65a3",  # noqa: E501
        "expected_raw_transaction": "0x03f8ec820539800285012a05f200833d090094095e7baea6a6c7c4c2dfeb977efac326af552d87830186a000f85bf85994095e7baea6a6c7c4c2dfeb977efac326af552d87f842a00000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000010ae1a001a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d801a0d10cbee5653bdc5c2b0bafe8a88efafc6d9f5123815178783a4d7820937917faa03040e5f117d33a7873d8bfa8fad8bf5d1163db2ce4e3de5ea414a45e199b5b2d",  # noqa: E501
        "transaction": {
            "accessList": (
                {
                    "address": "0x095E7BAea6a6c7c4c2DfeB977eFac326aF552d87",
                    "storageKeys": (
                        "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                        "0x0000000000000000000000000000000000000000000000000000000000000001",  # noqa: E501
                    ),
                },
            ),
            "blobVersionedHashes": [
                "0x01a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8"
            ],
            "data": "0x00",
            "gas": "0x3d0900",
            "maxFeePerBlobGas": "0x0a",
            "maxFeePerGas": "0x012a05f200",
            "maxPriorityFeePerGas": "0x02",
            "nonce": "0x00",
            "to": "0x095E7BAea6a6c7c4c2DfeB977eFac326aF552d87",
            "value": "0x0186a0",
            "chainId": "0x539",
            "v": "0x1",
            "r": "0xd10cbee5653bdc5c2b0bafe8a88efafc6d9f5123815178783a4d7820937917fa",
            "s": "0x3040e5f117d33a7873d8bfa8fad8bf5d1163db2ce4e3de5ea414a45e199b5b2d",
        },
    },
]

TEST_CASE_IDS = [
    "al-non-empty-list",
    "al-empty-list",
    "al-many-lists",
    "al-as-list-not-tuple",
    "al-no-explicit-type",
    "df-1",
    "df-2-int-values-and-access-list",
    "df-no-explicit-type",
    "blob-no-access-list",
    "blob-int-values-and-access-list",
    "blob-no-explicit-type",
]


@pytest.mark.parametrize(
    "test_case",
    TEST_CASES,
    ids=TEST_CASE_IDS,
)
def test_hash(test_case):
    expected = test_case["expected_hash"]
    transaction = TypedTransaction.from_dict(test_case["transaction"])
    hash = transaction.hash()
    actual = HexBytes(hash).to_0x_hex()
    assert actual == expected


@pytest.mark.parametrize("test_case", TEST_CASES, ids=TEST_CASE_IDS)
def test_encode(test_case):
    expected = test_case["expected_raw_transaction"]
    transaction = TypedTransaction.from_dict(test_case["transaction"])
    raw_transaction = transaction.encode()
    actual = HexBytes(raw_transaction).to_0x_hex()
    assert actual == expected


@pytest.mark.parametrize("test_case", TEST_CASES, ids=TEST_CASE_IDS)
def test_decode_encode(test_case):
    raw_transaction = test_case["expected_raw_transaction"]
    # Decode.
    actual = TypedTransaction.from_bytes(HexBytes(raw_transaction))
    assert isinstance(actual.transaction, test_case["expected_type"])
    expected = TypedTransaction.from_dict(test_case["transaction"])
    assert actual.as_dict() == expected.as_dict()
    # Re-encode.
    encoded = actual.encode()
    assert HexBytes(encoded) == HexBytes(raw_transaction)
