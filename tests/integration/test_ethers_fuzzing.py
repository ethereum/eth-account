import pytest
import subprocess

from hypothesis import (
    given,
    settings,
    strategies as st,
)

from eth_account import (
    Account,
)
from eth_account.hdaccount.mnemonic import (
    VALID_ENTROPY_SIZES,
    Mnemonic,
)

Account.enable_unaudited_hdwallet_features()

language_st = st.sampled_from(Mnemonic.list_languages())

seed_st = (
    st.binary(min_size=min(VALID_ENTROPY_SIZES), max_size=max(VALID_ENTROPY_SIZES))
    .filter(lambda x: len(x) in VALID_ENTROPY_SIZES)
    .filter(lambda s: int.from_bytes(s, byteorder="big") != 0)
)

node_st = st.tuples(st.integers(min_value=0, max_value=2**31 - 1), st.booleans())
path_st = (
    st.lists(node_st, min_size=0, max_size=10)
    .map(lambda nodes: list(str(n[0]) + ("" if n[1] else "'") for n in nodes))
    .map(lambda nodes: "m" + ("/" + "/".join(nodes) if nodes else ""))
)


@given(seed=seed_st, language=language_st, account_path=path_st)
@settings(deadline=1000)
@pytest.mark.compatibility
def test_compatibility(seed, language, account_path):
    mnemonic = Mnemonic(language).to_mnemonic(seed)
    acct = Account.from_mnemonic(mnemonic, account_path=account_path)
    # NOTE Must do `cd tests/integration/js-scripts && npm install -g .
    ethers_cli = subprocess.run(
        [
            "node",
            "tests/integration/js-scripts/ethers-mnemonic-fuzzing",
            "-m",
            mnemonic,
            "-l",
            language,
            "-p",
            account_path,
        ],
        capture_output=True,
    )
    if ethers_cli.stderr:
        raise OSError(ethers_cli.stderr.decode("utf-8"))
    ethers_address = ethers_cli.stdout.decode("utf-8").strip()
    assert acct.address == ethers_address
