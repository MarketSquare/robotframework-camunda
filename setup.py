#!/usr/bin/env python

from setuptools import setup, find_packages

name = "Deutsche Post Adress GmbH & Co. KG"

setup(
    name="robotframework-camunda",
    version="0.1.0",
    description="Keywords for camunda rest api",
    long_description="Keywords for camunda rest api, leading open source workflow engine.",
    author=name,
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Framework :: Robot Framework",
    ],
    license="Apache License, Version 2.0",
    install_requires=["robotframework", "requests", "frozendict", 'camunda-external-task-client-python3>=3.0,<3.1'],
    include_package_data=True,
)