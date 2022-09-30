Release Notes
=============

.. towncrier release notes start

eth-account v0.7.0 (2022-08-17)
-------------------------------

Bugfixes
~~~~~~~~

- bump ansi-regex to 5.0.1 to fix minor ReDos vulnerability (`#129 <https://github.com/ethereum/eth-account/issues/129>`__)
- Enable lint runs again on CI (`#166 <https://github.com/ethereum/eth-account/issues/166>`__)
- fix DoS-able regex pattern (`#178 <https://github.com/ethereum/eth-account/issues/178>`__)
- Allow towncrier to build the release notes again (`#185 <https://github.com/ethereum/eth-account/issues/185>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Add example to generate multiple accounts from a mnemonic (`#153 <https://github.com/ethereum/eth-account/issues/153>`__)
- Pin Jinja2 at >=3.0.0,<3.1.0; pin towncrier==18.5.0; open up Sphinx requirement to allow >=1.6.5,<5. (`#156 <https://github.com/ethereum/eth-account/issues/156>`__)
- added missing quotes to readme dev environment setup example (`#172 <https://github.com/ethereum/eth-account/issues/172>`__)


Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#79 <https://github.com/ethereum/eth-account/issues/79>`__, `#155 <https://github.com/ethereum/eth-account/issues/155>`__, `#162 <https://github.com/ethereum/eth-account/issues/162>`__, `#164 <https://github.com/ethereum/eth-account/issues/164>`__, `#165 <https://github.com/ethereum/eth-account/issues/165>`__


Breaking changes
~~~~~~~~~~~~~~~~

- Change bitarray dependency requirement to be >=2.4,<3 since 2.4 has wheels for all platform types. (`#154 <https://github.com/ethereum/eth-account/issues/154>`__)
- Fix errors in EIP-712 signing (`#175 <https://github.com/ethereum/eth-account/issues/175>`__)


eth-account v0.6.1 (2022-02-24)
-------------------------------

Bugfixes
~~~~~~~~

- Allow encoding of structured data containing ``bytes`` (`#91 <https://github.com/ethereum/eth-account/issues/91>`__)


Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#68 <https://github.com/ethereum/eth-account/issues/68>`__, `#144 <https://github.com/ethereum/eth-account/issues/144>`__


eth-account v0.6.0 (2022-01-20)
-------------------------------

Features
~~~~~~~~

- Update dependencies:
  - eth-abi
  - eth-keyfile
  - eth-keys
  - eth-rlp
  - pyrlp
  - eth-utils (`#138 <https://github.com/ethereum/eth-account/issues/138>`__)
- Add support for Python 3.9 and 3.10 (`#139 <https://github.com/ethereum/eth-account/issues/139>`__)


Deprecations and Removals
~~~~~~~~~~~~~~~~~~~~~~~~~

- Drop support for Python 3.6 (`#139 <https://github.com/ethereum/eth-account/issues/139>`__)


eth-account v0.5.9 (2022-08-04)
-------------------------------

Bugfixes
~~~~~~~~

- fix DoS-able regex pattern (`#178 <https://github.com/ethereum/eth-account/issues/178>`__)


Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#183 <https://github.com/ethereum/eth-account/issues/183>`__, `#184 <https://github.com/ethereum/eth-account/issues/184>`__


eth-account v0.5.8 (2022-06-06)
-------------------------------

Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#163 <https://github.com/ethereum/eth-account/issues/163>`__, `#168 <https://github.com/ethereum/eth-account/issues/168>`__

eth-account v0.5.7 (2022-01-27)
-------------------------------

Features
~~~~~~~~

- Add support for Python 3.9 and 3.10 (`#139 <https://github.com/ethereum/eth-account/issues/139>`__)


Bugfixes
~~~~~~~~

- ``recover_message`` now raises an ``eth_keys.exceptions.BadSignature`` error if the v, r, and s points are invalid (`#142 <https://github.com/ethereum/eth-account/issues/142>`__)


eth-account v0.5.6 (2021-09-22)
-------------------------------

Features
~~~~~~~~

- An explicit transaction type is no longer required for signing a transaction if we can implicitly determine the transaction type from the transaction parameters (`#125 <https://github.com/ethereum/eth-account/issues/125>`__)


Bugfixes
~~~~~~~~

- When signing a transaction, the regular JSON-RPC structure is now expected as input and is converted to the appropriate rlp transaction structure when signing (`#125 <https://github.com/ethereum/eth-account/issues/125>`__)
- Fix string interpolation in ``ValidationError`` message of _hash_eip_191_message (`#128 <https://github.com/ethereum/eth-account/issues/128>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Updated docs for sign_transaction to show that transaction type can be implicitly determined based on transaction parameters if one is not provided (`#126 <https://github.com/ethereum/eth-account/issues/126>`__)
- Add ``encode_defunct`` to list of example message encoders (`#127 <https://github.com/ethereum/eth-account/issues/127>`__)


eth-account v0.5.5 (2021-07-21)
-------------------------------

Features
~~~~~~~~

- Added support for EIP-2718 (Typed Transaction) and EIP-2939 (Access List Transaction) (`#115 <https://github.com/ethereum/eth-account/issues/115>`__)
- Added support for EIP-1559 (Dynamic Fee Transaction) (`#117 <https://github.com/ethereum/eth-account/issues/117>`__)


Bugfixes
~~~~~~~~

- Structured messages (EIP-712) new permit leaving some (but not all) domain fields undefined. (`#72 <https://github.com/ethereum/eth-account/issues/72>`__)


Internal Changes - for eth-account Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Upgrade project template, of note: a new mypy & pydocstyle, and types being exported correctly. (`#121 <https://github.com/ethereum/eth-account/issues/121>`__)


Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#116 <https://github.com/ethereum/eth-account/issues/116>`__


v0.5.3 (2020-08-31)
-------------------

Performance improvements
~~~~~~~~~~~~~~~~~~~~~~~~

- RLP encoding/decoding speedup by using rlp v2alpha1, which has a rust implementation. (`#104 <https://github.com/ethereum/eth-account/issues/104>`__)


v0.5.2 (2020-04-30)
------------------------------

Bugfixes
~~~~~~~~

- Makes sure that the raw txt files needed for Mnemonics get packaged with the release. (`#99 <https://github.com/ethereum/eth-account/issues/99>`__)


v0.5.1
----------------

Released 2020-04-23

- Fix a crash in signing typed messages with arrays
  `#97 <https://github.com/ethereum/eth-account/pull/97>`_
- Replace attrdict with NamedTuple to silence a deprecation warning
  `#76 <https://github.com/ethereum/eth-account/pull/76>`_
- Run more doctests & improve docs
  `#94 <https://github.com/ethereum/eth-account/pull/94>`_

v0.5.0
----------------

Released 2020-03-30

- Add Python 3.8 support
  `#86 <https://github.com/ethereum/eth-account/pull/86>`_
- Add opt-in support for Mnemonic seed phrases
  `#87 <https://github.com/ethereum/eth-account/pull/87>`_
  (NOTE: This API is unaudited and likely to change)
- Dependency change: support eth-keys v0.3.*
  `#69 <https://github.com/ethereum/eth-account/pull/69>`_

v0.4.0
----------------

Released 2019-05-06

- BREAKING CHANGE: drop python 3.5 (and therefore pypy3 support).
  `#60 <https://github.com/ethereum/eth-account/pull/60>`_ (includes other housekeeping)
- New message signing API: :meth:`~eth_account.account.Account.sign_message` and
  ``recover_message``. `#61 <https://github.com/ethereum/eth-account/pull/61>`_

  - New :meth:`eth_account.messages.encode_intended_validator` for EIP-191's Intended Validator
    message-signing format.
    `#56 <https://github.com/ethereum/eth-account/pull/56>`_
  - New :meth:`eth_account.messages.encode_structured_data` for EIP-712's Structured Data
    message-signing format.
    `#57 <https://github.com/ethereum/eth-account/pull/57>`_
- Add optional param iterations to :meth:`~eth_account.account.Account.encrypt`
  `#52 <https://github.com/ethereum/eth-account/pull/52>`_
- Add optional param kdf to :meth:`~eth_account.account.Account.encrypt`, plus env var
  :envvar:`ETH_ACCOUNT_KDF`. Default kdf switched from hmac-sha256 to scrypt.
  `#38 <https://github.com/ethereum/eth-account/pull/38>`_
- Accept "to" addresses formatted as :class:`bytes` in addition to checksummed, hex-encoded.
  `#36 <https://github.com/ethereum/eth-account/pull/36>`_

v0.3.0
----------------

Released July 24, 2018

- Support :class:`eth_keys.datatypes.PrivateKey` in params that accept a private key.
- New docs for :doc:`eth_account.signers`
- Under the hood: add a new :class:`~eth_account.signers.base.BaseAccount` abstract class, so
  that upcoming signing classes can implement it (be on the lookout for upcoming hardware wallet
  support)

v0.2.3
----------------

Released May 27, 2018

- Implement __eq__ and __hash__ for :class:`~eth_account.signers.local.LocalAccount`, so that
  accounts can be used in :class:`set`, or as keys in :class:`dict`, etc.

v0.2.2
----------------

Released Apr 25, 2018

- Compatibility with pyrlp v0 and v1

v0.2.1
----------------

Released Apr 23, 2018

- Accept 'from' in signTransaction, if it matches the sending private key's address

v0.2.0 (stable)
----------------

Released Apr 19, 2018

- Audit cleanup is complete
- Stopped requiring chainId, until tooling to automatically derive it gets better
  (Not that transactions without chainId are potentially replayable on fork chains)

v0.2.0-alpha.0
--------------

Released Apr 6, 2018

- Ability to sign an already-hashed message
- Moved ``eth_sign``-style message hashing to :meth:`eth_account.messages.defunct_hash_message`
- Stricter transaction input validation, and better error messages.
  Including: `to` field must be checksummed.
- PyPy3 support & tests
- Upgrade dependencies
- Moved non-public interfaces to `internal` module
- Documentation

  - use ``getpass`` instead of typing in password manually
  - :class:`eth_account.signers.local.LocalAccount` attributes
  - readme improvements
  - more


v0.1.0-alpha.2
--------------

- Imported the local signing code from web3.py's :class:`w3.eth.account <web3.account.Account>`
- Imported documentation and added more
- Imported tests and pass them

v0.1.0-alpha.1
--------------

- Launched repository, claimed names for pip, RTD, github, etc
