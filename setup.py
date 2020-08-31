#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    setup,
    find_packages,
)

extras_require = {
    'test': [
        "hypothesis>=4.18.0,<5",
        "pytest>=4.4.0,<5",
        "pytest-xdist",
        "tox>=2.9.1,<3",
    ],
    'lint': [
        "flake8==3.7.9",
        "isort>=4.2.15,<5",
        "mypy==0.701",
        "pydocstyle>=3.0.0,<4",
    ],
    'doc': [
        "Sphinx>=1.6.5,<2",
        "sphinx_rtd_theme>=0.1.9",
        "towncrier>=19.2.0, <20",
    ],
    'dev': [
        "bumpversion>=0.5.3,<1",
        "pytest-watch>=4.1.0,<5",
        "wheel",
        "twine",
        "ipython",
    ],
}

extras_require['dev'] = (
    extras_require['dev'] +  # noqa: W504
    extras_require['test'] +  # noqa: W504
    extras_require['lint'] +  # noqa: W504
    extras_require['doc']
)


with open('./README.md') as readme:
    long_description = readme.read()


setup(
    name='eth-account',
    # *IMPORTANT*: Don't manually change the version here. Use `make bump`, as described in readme
    version='0.5.3',
    description="""eth-account: Sign Ethereum transactions and messages with local private keys""",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='The Ethereum Foundation',
    author_email='snakecharmers@ethereum.org',
    url='https://github.com/ethereum/eth-account',
    include_package_data=True,
    package_data={"eth_account": ["hdaccount/wordlist/*.txt"]},
    install_requires=[
        "bitarray>=1.2.1,<1.3.0",
        "eth-abi>=2.0.0b7,<3",
        "eth-keyfile>=0.5.0,<0.6.0",
        "eth-keys>=0.2.1,<0.4.0,!=0.3.2",
        "eth-rlp>=0.1.2,<1",
        "eth-utils>=1.3.0,<2",
        "hexbytes>=0.1.0,<1",
        "rlp>=1.0.0,<=2.0.0.alpha-1"
    ],
    python_requires='>=3.6, <4',
    extras_require=extras_require,
    py_modules=['eth_account'],
    license="MIT",
    zip_safe=False,
    keywords='ethereum',
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
