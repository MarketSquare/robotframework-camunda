#!/usr/bin/env python

from setuptools import setup, find_packages
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

name = "Deutsche Post Adress GmbH & Co. KG"

setup(
    name="robotframework-camunda",
    version="0.3.4",
    description="Keywords for camunda rest api, leading open source workflow engine.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=name,
    author_email="markus.stahl@postadress.de",
    url=os.environ['CI_PROJECT_URL'],
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Framework :: Robot Framework",
    ],
    license="Apache License, Version 2.0",
    install_requires=["robotframework", "requests", "frozendict", 'camunda-external-task-client-python3>=3.0,<3.1'],
    include_package_data=True,
)