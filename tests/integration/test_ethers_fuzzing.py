import pytest
import subprocess

from hypothesis import (
    given,
    strategies as st,
    settings,
)

from eth_account import (
    Account,
)
from eth_account.hdaccount.mnemonic import (
    Mnemonic,
)


language_st = st.sampled_from(Mnemonic.list_languages())

seed_st = st.binary(min_size=16, max_size=32) \
    .filter(lambda x: len(x) in (16, 20, 24, 28, 32)) \
    .filter(lambda s: int.from_bytes(s, byteorder="big") != 0)


@given(seed=seed_st, language=language_st)
@settings(deadline=500)
@pytest.mark.compatibility
def test_compatibility(seed, language):
    mnemonic = Mnemonic(language).to_mnemonic(seed)
    acct = Account.from_mnemonic(mnemonic)
    # NOTE Must do `cd ethers-cli && npm install -g .
    ethers_cli = subprocess.run(
        ['ethers-cli', '-m', mnemonic, '-l', language],
        capture_output=True,
    )
    ethers_address = ethers_cli.stdout.decode("utf-8").strip()
    assert acct.address == ethers_address
