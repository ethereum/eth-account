#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    setup,
    find_packages,
)


setup(
    name='eth-account',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version='0.1.0-alpha.1',
    description="""eth-account: private key signing and recovery in python""",
    long_description_markdown_filename='README.md',
    author='Jason Carver',
    author_email='ethcalibur+pip@gmail.com',
    url='https://github.com/ethereum/eth-account',
    include_package_data=True,
    install_requires=[
        # "eth-abi>=0.5.0,<1.0.0",
        "eth-keyfile>=0.4.0,<1.0.0",
        "eth-keys>=0.1.0b4,<0.2.0",
        "eth-utils>=0.7.1,<1.0.0",
        # "lru-dict>=1.1.6,<2.0.0",
        # "pysha3>=1.0.0,<2.0.0",
        # "requests>=2.16.0,<3.0.0",
        "rlp>=0.4.7,<1.0.0",
    ],
    setup_requires=['setuptools-markdown'],
    extras_require={
        'tester': [
            "pytest==3.3.2",
            "tox>=2.9.1,<3",
        ],
        'linter': [
            "flake8==3.4.1",
            "isort>=4.2.15,<5",
        ],
        'dev': [
            "pytest-xdist",
            "bumpversion>=0.5.3,<1",
            "eth-account[tester]",
            "eth-account[linter]",
        ],
    },
    py_modules=['eth_account'],
    license="MIT",
    zip_safe=False,
    keywords='ethereum',
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
