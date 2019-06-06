Release Notes
=============

v0.5.0
----------------

Unreleased

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
