#!/usr/bin/env python

from setuptools import setup, find_packages
import re
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

name = "Deutsche Post Adress GmbH & Co. KG"

version_regex = r"^v(?P<version>\d*\.\d*\.\d*$)"
version = os.environ.get('CI_COMMIT_TAG', f'0.{os.environ.get("CI_COMMIT_REF_NAME","8.0a1")}')
full_version_match = re.fullmatch(version_regex, version)
if full_version_match:
    version = full_version_match.group('version')

setup(
    name="robotframework-camunda",
    version=version,
    description="Keywords for camunda rest api, leading open source workflow engine.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=name,
    author_email="markus.stahl@postadress.de",
    url=os.environ.get('CI_PROJECT_URL'),
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
    install_requires=["robotframework", "requests", "frozendict", 'generic-camunda-client'],
    include_package_data=True,
)