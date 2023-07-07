from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

setup(
    name="async-worker",
    version="0.20.1",
    description="Microframework para escrever workers assíncronos em Python",
    long_description=open(f"{here}/README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/async-worker/async-worker",
    # Author details
    author="Dalton Barreto",
    author_email="daltonmatos@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    install_requires=[
        "aioamqp==0.15.0",
        "aiologger==0.7.0",
        "pydantic >= 0.32.2, <= 1.8",
        "cached-property==1.5.1",
        "aiohttp==3.8.4",
        "prometheus_client==0.7.1",
    ],
    entry_points={},
)
