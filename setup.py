import os
from setuptools import setup, find_packages

from easyqueue import __VERSION__


BASE_PATH = os.path.dirname(__file__)


setup(
    name='easyqueue',
    version=__VERSION__,
    author='Diogo Magalhães Martins',
    author_email='magalhaesmartins@icloud.com',
    maintainer='Sieve',
    maintainer_email='ti@sieve.com.br',
    description="An easy way to handle amqp queues. Focus on your app logic, "
                "forget about the protocol.",
    url='https://bitbucket.org/sievetech/easyqueue',
    packages=find_packages(exclude=['easyqueue/tests']),
    install_requires=[
        "aioamqp==0.10.0"
    ],
    test_suite='easyqueue.tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
