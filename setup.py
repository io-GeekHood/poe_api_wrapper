import os

from setuptools import setup, find_packages

name = 'poe_api'
version = os.getenv('VERSION', '1')
description = 'poe bot graphql and wss connector'
url = 'https://git.io-GeekHood.com'
author = 'Ali Hashempourian'
author_email = 'hashempourian.a@gmail.com'


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name=name,
    version=version,
    description=description,

    url=url,
    author=author,
    author_email=author_email,

    packages=find_packages(),
    install_requires=requirements,

    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [f'{name}={name}.cmd:main'],
    },
)
