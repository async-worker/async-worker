import os
from setuptools import setup, find_packages

from easyqueue import __version__

BASE_PATH = os.path.dirname(__file__)
setup(
    name='easyqueue',
    version=__version__,
    description='Utils for every Sieve project',
    url='https://bitbucket.org/sievetech/easyqueue',
    packages=find_packages(exclude=['easyqueue/tests']),
    install_requires=[
        'amqp==2.1.4'
    ],
    test_suite='easyqueue.tests',
)
