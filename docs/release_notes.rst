Release Notes
=============

.. towncrier release notes start

eth-account v0.13.0 (2024-05-20)
--------------------------------

Bugfixes
~~~~~~~~

- Open up Pydantic dependency (`#271 <https://github.com/ethereum/eth-account/issues/271>`__)


Features
~~~~~~~~

- Expose TypedTransactions for public use (`#276 <https://github.com/ethereum/eth-account/issues/276>`__)


Internal Changes - for eth-account Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Merge template updates, notably adding python 3.12 support (`#274 <https://github.com/ethereum/eth-account/issues/274>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#275 <https://github.com/ethereum/eth-account/issues/275>`__


Removals
~~~~~~~~

- Remove ``signHash`` in favor of ``unsafe_sign_hash`` (`#260 <https://github.com/ethereum/eth-account/issues/260>`__)
- Remove ``messageHash`` in favor of ``message_hash`` (`#265 <https://github.com/ethereum/eth-account/issues/265>`__)
- Moved private ``_parsePrivateKey`` method to ``_parse_private_key`` (`#267 <https://github.com/ethereum/eth-account/issues/267>`__)
- Remove ``SignedTransaction``'s ``rawTransaction`` attribute in favor of ``raw_transaction`` (`#268 <https://github.com/ethereum/eth-account/issues/268>`__)
- Remove ``encode_structured_data`` in favor of ``encode_typed_data`` (`#269 <https://github.com/ethereum/eth-account/issues/269>`__)


eth-account v0.12.1 (2024-04-02)
--------------------------------

Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Update documentation to include blob transaction signing example. (`#258 <https://github.com/ethereum/eth-account/issues/258>`__)


eth-account v0.12.0 (2024-04-01)
--------------------------------

Bugfixes
~~~~~~~~

- Import cytoolz methods via eth_utils instead of cytoolz directly (`#251 <https://github.com/ethereum/eth-account/issues/251>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Add ``encode_typed_data`` to list of functions that return a ``SignableMessage`` (`#247 <https://github.com/ethereum/eth-account/issues/247>`__)


Features
~~~~~~~~

- Add support for type ``3``, ``BlobTransaction``, introduced by the Cancun network upgrade. (`#253 <https://github.com/ethereum/eth-account/issues/253>`__)


Internal Changes - for eth-account Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Bump deps to ``hexbytes>=1.2.0`` and ``eth-rlp>=2.1.0`` (`#254 <https://github.com/ethereum/eth-account/issues/254>`__)


eth-account v0.11.0 (2024-02-05)
--------------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Drop support for python 3.7 (`#248 <https://github.com/ethereum/eth-account/issues/248>`__)


Internal Changes - for eth-account Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Change older ``%`` and ``.format`` strings to use ``f-strings`` (`#245 <https://github.com/ethereum/eth-account/issues/245>`__)
- Merge template updates, notably use ``pre-commit`` for linting and change the name of the ``master`` branch to ``main`` (`#248 <https://github.com/ethereum/eth-account/issues/248>`__)


Removals
~~~~~~~~

- Remove deprecated ``signTransaction``, it has been replaced by ``sign_transaction`` (`#244 <https://github.com/ethereum/eth-account/issues/244>`__)


eth-account v0.10.0 (2023-10-30)
--------------------------------

Deprecations
~~~~~~~~~~~~

- Deprecate ``encode_structured_data`` in favor of new ``encode_typed_data`` (`#235 <https://github.com/ethereum/eth-account/issues/235>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Added usage notes and example for ``encode_structured_data`` (`#233 <https://github.com/ethereum/eth-account/issues/233>`__)


Features
~~~~~~~~

- Add new ``encode_typed_data`` to better handle EIP712 message signing (`#235 <https://github.com/ethereum/eth-account/issues/235>`__)
- Added option to call ``encode_typed_data`` with a single dict arg in addition to the existing 3-dict style (`#238 <https://github.com/ethereum/eth-account/issues/238>`__)
- Add ``sign_typed_data`` as a method of the ``Account`` class (`#239 <https://github.com/ethereum/eth-account/issues/239>`__)


Internal Changes - for eth-account Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Added tests for ``encode_structured_data`` for easier comparison with Metamask's SignTypedData (`#233 <https://github.com/ethereum/eth-account/issues/233>`__)
- Bump version for node and ethers.js in integration tests, update ethers usage to match (`#236 <https://github.com/ethereum/eth-account/issues/236>`__)
- Add ``build.os`` to readthedocs settings (`#237 <https://github.com/ethereum/eth-account/issues/237>`__)
- Add upper pin to ``hexbytes`` dependency to due incoming breaking change (`#240 <https://github.com/ethereum/eth-account/issues/240>`__)
- Add tests comparing output of signed EIP712 messages with metamask and ethers (`#241 <https://github.com/ethereum/eth-account/issues/241>`__)


eth-account v0.9.0 (2023-06-07)
-------------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- drop python3.6 support from setup (`#228 <https://github.com/ethereum/eth-account/issues/228>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- remove notices of Draft status for eips 712 and 191 (`#222 <https://github.com/ethereum/eth-account/issues/222>`__)


Features
~~~~~~~~

- Add support for Python 3.11 (`#212 <https://github.com/ethereum/eth-account/issues/212>`__)


Internal Changes - for eth-account Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Upgrade Node from v12.x to v18.x in tests (`#217 <https://github.com/ethereum/eth-account/issues/217>`__)
- pulled full new node_v18 install script (`#223 <https://github.com/ethereum/eth-account/issues/223>`__)
- bump versions for docs dependencies (`#224 <https://github.com/ethereum/eth-account/issues/224>`__)
- add sphinx_rtd_theme to docs/conf.py extensions list (`#225 <https://github.com/ethereum/eth-account/issues/225>`__)
- merge in updates from python project template (`#288 <https://github.com/ethereum/eth-account/issues/288>`__)


eth-account v0.8.0 (2022-12-15)
-------------------------------

Features
~~~~~~~~

- update all references to deprecated `eth_abi.encode_abi` to `eth_abi.encode` (`#200 <https://github.com/ethereum/eth-account/issues/200>`__)


Performance improvements
~~~~~~~~~~~~~~~~~~~~~~~~

- Reduce the number of pbkdf2 iterations to speed up tests (`#77 <https://github.com/ethereum/eth-account/issues/77>`__)


Deprecations and Removals
~~~~~~~~~~~~~~~~~~~~~~~~~

- remove deprecated methods that were noted to go in v0.5 (`#195 <https://github.com/ethereum/eth-account/issues/195>`__)


Internal Changes - for eth-account Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- add coverage reporting to pytest (`#192 <https://github.com/ethereum/eth-account/issues/192>`__)
- Use updated circleci Python images, fix Sphinx warning (`#194 <https://github.com/ethereum/eth-account/issues/194>`__)


Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#197 <https://github.com/ethereum/eth-account/issues/197>`__, `#198 <https://github.com/ethereum/eth-account/issues/198>`__, `#199 <https://github.com/ethereum/eth-account/issues/199>`__, `#202 <https://github.com/ethereum/eth-account/issues/202>`__, `#203 <https://github.com/ethereum/eth-account/issues/203>`__, `#204 <https://github.com/ethereum/eth-account/issues/204>`__, `#206 <https://github.com/ethereum/eth-account/issues/206>`__


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
