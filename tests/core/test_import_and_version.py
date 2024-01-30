def test_import_and_version():
    import eth_account

    assert isinstance(eth_account.__version__, str)
