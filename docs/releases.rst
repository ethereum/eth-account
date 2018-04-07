Release Notes
=============

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
  - :class:`eth_account.local.LocalAccount` attributes
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
