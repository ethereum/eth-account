Contributing
------------

Thank you for your interest in contributing! We welcome all contributions no matter
their size. Please read along to learn how to get started. If you get stuck, feel free
to ask for help in `Ethereum Python Discord server <https://discord.gg/GHryRvPB84>`_.

Setting the stage
~~~~~~~~~~~~~~~~~

To get started, fork the repository to your own github account, then clone it to your
development machine:

.. code:: sh

    git clone git@github.com:your-github-username/eth-account.git

Next, install the development dependencies with
`uv <https://docs.astral.sh/uv/>`_. The ``dev`` dependency group is installed
by default, so ``uv sync`` is enough for a local development environment.

.. code:: sh

    cd eth-account
    uv sync
    uv run prek install

Running the tests
~~~~~~~~~~~~~~~~~

A great way to explore the code base is to run the tests.

We can then run the core tests with:

.. code:: sh

    pytest tests/core

To run the integration test cases, we need to install node and the custom cli tool as follows:

.. code:: sh

    # on Ubuntu
    chmod +x ./tests/integration/js-scripts/setup_node_v22.sh
    ./tests/integration/js-scripts/setup_node_v22.sh  # As sudo
    apt-get install -y nodejs  # As sudo
    cd tests/integration/js-scripts
    npm install

We can then run all tests with:

.. code:: sh

    pytest tests

Code Style
~~~~~~~~~~

We use `prek <https://prek.j178.dev>`_ to enforce a consistent code style across
the library. This tool runs automatically with every commit, but you can also run it
manually with:

.. code:: sh

    make lint

If you need to make a commit that skips the ``prek`` checks, you can do so with
``git commit --no-verify``.

This library uses type hints, which are enforced by the ``mypy`` tool (part of the
``prek`` checks). All new code is required to land with type hints, with the
exception of code within the ``tests`` directory.

Documentation
~~~~~~~~~~~~~

Good documentation will lead to quicker adoption and happier users. Please check out our
guide on
`how to create documentation for the Python Ethereum ecosystem <https://github.com/ethereum/snake-charmers-tactical-manual/blob/main/documentation.md>`_.

Pull Requests
~~~~~~~~~~~~~

It's a good idea to make pull requests early on. A pull request represents the start of
a discussion, and doesn't necessarily need to be the final, finished submission.

GitHub's documentation for working on pull requests is
`available here <https://docs.github.com/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests>`_.

Once you've made a pull request, take a look at the Circle CI build status in the
GitHub interface and make sure all tests are passing. In general pull requests that
do not pass the CI build yet won't get reviewed unless explicitly requested.

If the pull request introduces changes that should be reflected in the release notes,
please add a newsfragment file as explained
`here <https://github.com/ethereum/eth-account/blob/main/newsfragments/README.md>`_.

If possible, the change to the release notes file should be included in the commit that
introduces the feature or bugfix.

Releasing
~~~~~~~~~

Releases are typically done from the ``main`` branch, except when releasing a beta (in
which case the beta is released from ``main``, and the previous stable branch is
released from said branch).

Final review before each release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before releasing a new version, run the test suite from the release branch:

.. code:: sh

    git checkout main && git pull
    uv run --group test pytest tests/core

Review the documentation that will get published:

.. code:: sh

    uv run --group docs sphinx-apidoc -o docs/ . "conftest*" "tests" "tests/*"
    uv run --group docs sphinx-build -W -b html docs docs/_build/html
    uv run --group docs sphinx-build -W -b doctest docs docs/_build/doctest

Publish a release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After confirming that the release package looks okay, create a GitHub Release for the
version being published. The release tag is the canonical version source:
``setuptools-scm`` derives the package version from that tag, and the release workflow
builds and publishes the package to PyPI using trusted publishing.

Release notes are maintained through GitHub Releases.
