# eth-account

[![Join the conversation on Discord](https://img.shields.io/discord/809793915578089484?color=blue&label=chat&logo=discord&logoColor=white)](https://discord.gg/GHryRvPB84)
[![Test Status](https://github.com/ApeWorX/eth-account/actions/workflows/test.yaml/badge.svg)](https://github.com/ApeWorX/eth-account/actions/workflows/test.yaml)
[![PyPI version](https://badge.fury.io/py/eth-account.svg)](https://badge.fury.io/py/eth-account)
[![Python versions](https://img.shields.io/pypi/pyversions/eth-account.svg)](https://pypi.python.org/pypi/eth-account)
[![Docs build](https://readthedocs.org/projects/eth-account/badge/?version=latest)](https://eth-account.readthedocs.io/en/latest/?badge=latest)

Sign Ethereum transactions and messages with local private keys

## Differences from upstream eth-account

This fork is based on eth-account 0.14.0 and differs from the upstream package in the following ways:

- `ckzg` is optional instead of a runtime dependency. Standard account, message, and transaction
  signing works without installing it. Blob transaction commitment and proof generation requires
  installing the package with the `ckzg` extra: `eth-account[ckzg]`.
- `ckzg` is imported only when blob commitments or proofs are generated, so importing
  `eth_account` does not require the native extension.
- The minimum `eth-utils` version is 5.3.1, allowing the fork to coexist with packages that have
  not yet adopted eth-utils 6.
- CI runs linting, type checks, documentation checks, and tests on Python 3.14 only. The package
  metadata continues to allow Python 3.10 and newer, but those older versions are not tested by
  this fork's CI.

Read the [documentation](https://eth-account.readthedocs.io/).

View the [change log](https://eth-account.readthedocs.io/en/latest/release_notes.html).

## Installation

```sh
python -m pip install eth-account
```
