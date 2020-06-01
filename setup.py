# Always prefer setuptools over distutils
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

setup(
    name="async-worker",
    version="0.15.0",
    description="Microframework para escrever workers assíncronos em Python",
    long_description="Microframework para escrever workers assíncronos em Python",
    url="https://github.com/b2wdigital/async-worker",
    # Author details
    author="Dalton Barreto",
    author_email="daltonmatos@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    install_requires=[
        "aioamqp==0.14.0",
        "aiologger==0.5.0",
        "pydantic>=0.32.2, <2.0",
        "cached-property==1.5.1",
        "aiohttp==3.6.2",
        "prometheus_client==0.7.1",
    ],
    entry_points={},
)
