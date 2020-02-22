from hypothesis import (
    given,
    settings,
    strategies as st,
)
import pytest
import subprocess

from eth_account import (
    Account,
)
from eth_account.hdaccount.mnemonic import (
    VALID_ENTROPY_SIZES,
    Mnemonic,
)

Account.enable_unaudited_features()

language_st = st.sampled_from(Mnemonic.list_languages())

seed_st = st.binary(min_size=min(VALID_ENTROPY_SIZES), max_size=max(VALID_ENTROPY_SIZES)) \
    .filter(lambda x: len(x) in VALID_ENTROPY_SIZES) \
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
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if ethers_cli.stderr:
        raise IOError(ethers_cli.stderr.decode("utf-8"))
    ethers_address = ethers_cli.stdout.decode("utf-8").strip()
    assert acct.address == ethers_address
