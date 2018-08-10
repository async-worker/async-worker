import os
from setuptools import setup, find_packages


BASE_PATH = os.path.dirname(__file__)

__version__ = '1.2.1-rc1'


setup(
    name='easyqueue',
    version=__version__,
    author='Diogo Magalhães Martins',
    author_email='magalhaesmartins@icloud.com',
    maintainer='Sieve',
    maintainer_email='ti@sieve.com.br',
    description="An easy way to handle amqp queues. Focus on your app logic, "
                "forget about the protocol.",
    url='https://bitbucket.org/sievetech/easyqueue',
    packages=find_packages(exclude=['easyqueue/tests']),
    install_requires=[
        "aioamqp==0.11.0"
    ],
    test_suite='easyqueue.tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)
