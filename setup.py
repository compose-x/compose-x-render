#!/usr/bin/env python
#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2021 John Mille <john@compose-x.io>

"""The setup script."""

import os
import re
from setuptools import setup, find_packages

DIR_HERE = os.path.abspath(os.path.dirname(__file__))
# REMOVE UNSUPPORTED RST syntax
REF_REGX = re.compile(r"(\:ref\:)")

try:
    with open(f"{DIR_HERE}/README.rst", encoding="utf-8") as readme_file:
        readme = readme_file.read()
        readme = REF_REGX.sub("", readme)
except FileNotFoundError:
    readme = "Compose-X - Render"

try:
    with open(f"{DIR_HERE}/HISTORY.rst", encoding="utf-8") as history_file:
        history = history_file.read()
except FileNotFoundError:
    history = "Latest packaged version."

requirements = []
try:
    with open(f"{DIR_HERE}/requirements.txt", "r") as req_fd:
        for line in req_fd:
            requirements.append(line.strip())
except FileNotFoundError:
    requirements = []

test_requirements = []
try:
    with open(f"{DIR_HERE}/requirements_dev.txt", "r") as req_fd:
        for line in req_fd:
            test_requirements.append(line.strip())
except FileNotFoundError:
    print("Failed to load dev requirements. Skipping")

requirements = []
setup_requirements = [
    "pytest-runner",
]
test_requirements = [
    "pytest>=3",
]

setup(
    author="John Mille",
    author_email="john@compose-x.io",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Tool to compile compose files with top level extension fields",
    entry_points={
        "console_scripts": [
            "compose-x-render=compose_x_render.cli:main",
            "ecs-compose-x-render=compose_x_render.cli:main",
        ],
    },
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords="compose_x_render",
    name="compose_x_render",
    packages=find_packages(include=["compose_x_render", "compose_x_render.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/compose-x/compose_x_render",
    version="0.1.0",
    zip_safe=False,
)
