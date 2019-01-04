# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name="async-worker",
    version="0.7.0-rc3",
    description="Microframework para escrever consumers para RabbitMQ",
    long_description="Microframework para escrever consumers para RabbitMQ",
    url="https://github.com/B2W-BIT/async-worker",
    # Author details
    author="Dalton Barreto",
    author_email="daltonmatos@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    install_requires=[
        "easyqueue==2.0.0-rc1",
        "simple-json-logger==0.2.3",
        "pydantic==0.14",
        "cached-property==1.5.1",
        "aiohttp==3.4.4",
    ],
    entry_points={},
)
