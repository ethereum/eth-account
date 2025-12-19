# go-kzg-verify

A Go utility that generates signed EIP-7594 blob transaction test vectors using go-ethereum's KZG implementation. These test vectors are used to verify that eth-account's Python implementation produces identical results.

## Purpose

This tool reads blob test data from the [consensus-spec-tests](https://github.com/ethereum/consensus-spec-tests) repository and:

1. Computes KZG commitments and versioned hashes for each blob
1. Computes cell proofs using EIP-7594's `compute_cells_and_kzg_proofs`
1. Creates and signs a blob transaction (type 3) with the computed data
1. Outputs the results as JSON for comparison with eth-account's output

## Usage

```bash
./go-kzg-verify <consensus-spec-tests-dir> <output-file>
```

### Arguments

- `consensus-spec-tests-dir`: Path to a directory containing `*_valid_*/data.yaml` test files from consensus-spec-tests (specifically the `compute_cells_and_kzg_proofs` tests)
- `output-file`: Path where the JSON output will be written

### Example

```bash
./go-kzg-verify ./consensus-spec-tests/tests/general/deneb/kzg/compute_cells_and_kzg_proofs/small ./output.json
```

## Output Format

The tool outputs a JSON array with entries for each test case:

```json
[
  {
    "test_name": "compute_cells_and_kzg_proofs_case_valid_0",
    "blob": "0x...",
    "commitment": "0x...",
    "versioned_hash": "0x01...",
    "cell_proofs": ["0x...", ...],
    "signed_transaction_hex": "0x03..."
  }
]
```

## Transaction Details

The signed transactions use these fixed parameters (matching eth-account test constants):

| Field                | Value                                      |
| -------------------- | ------------------------------------------ |
| Chain ID             | 1                                          |
| Nonce                | 1                                          |
| Max Priority Fee     | 50 wei                                     |
| Max Fee              | 1000 wei                                   |
| Gas Limit            | 100,000                                    |
| To                   | 0x45Ae5777c9b35Eb16280e423b0d7c91C06C66B58 |
| Value                | 1 wei                                      |
| Data                 | 0x52fdfc072182654f                         |
| Max Fee Per Blob Gas | 100 wei                                    |
| Private Key          | 0x4646...4646 (32 bytes of 0x46)           |

## Building

Requires Go 1.24+:

```bash
cd go-kzg-verify
go build -o go-kzg-verify
```

## Dependencies

- [go-eth-kzg](https://github.com/crate-crypto/go-eth-kzg) - KZG cryptography (EIP-7594 support)
- [go-ethereum](https://github.com/ethereum/go-ethereum) - RLP encoding, signing, and Ethereum types
