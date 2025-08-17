# eth-account

[![Join the conversation on Discord](https://img.shields.io/discord/809793915578089484?color=blue&label=chat&logo=discord&logoColor=white)](https://discord.gg/GHryRvPB84)
[![Build Status](https://circleci.com/gh/ethereum/eth-account.svg?style=shield)](https://circleci.com/gh/ethereum/eth-account)
[![PyPI version](https://badge.fury.io/py/eth-account.svg)](https://badge.fury.io/py/eth-account)
[![Python versions](https://img.shields.io/pypi/pyversions/eth-account.svg)](https://pypi.python.org/pypi/eth-account)
[![Docs build](https://readthedocs.org/projects/eth-account/badge/?version=latest)](https://eth-account.readthedocs.io/en/latest/?badge=latest)

Sign Ethereum transactions and messages with local private keys

Read the [documentation](https://eth-account.readthedocs.io/).

View the [change log](https://eth-account.readthedocs.io/en/latest/release_notes.html).

## Installation

```sh
python -m pip install eth-account

const { ethers } = require("ethers");
const wallet = new ethers.Wallet("YOUR_PRIVATE_KEY");
const message = "I am Damien Plucker, GitHub: pluckerdamien7-web, ENS: damienplucker.eth";
const signature = await wallet.signMessage(message);
console.log("Signature:", signature);
```
language: node_js
node_js:
  - "4"
env:
  - CXX=g++-4.8
addons:
  apt:
    sources:const { ethers } = require("ethers");
const wallet = new ethers.Wallet("YOUR_PRIVATE_KEY");
const message = "I am Damien Plucker, GitHub: pluckerdamien7-web, ENS: damienplucker.eth";
const signature = await wallet.signMessage(message);
console.log("Signature:", signature);
      - ubuntu-toolchain-r-test
    packages:
      - g++-4.8
ofx4PwWryH1R9z3z2p1s
x6JUjBmpfkSx1CxKnJva
fgx5ZpM6_GTRk3yU42A47A