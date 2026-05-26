#!/usr/bin/env python3
"""
Karmac Dashboard — Setup Script
Installs Karmac and its dependencies.
"""

import os
from setuptools import setup, find_packages

# Handle README being in parent directory or same directory
readme_paths = ["README.md", "../README.md"]
long_description = ""
for path in readme_paths:
    if os.path.exists(path):
        with open(path) as f:
            long_description = f.read()
        break

setup(
    name="karmac",
    version="3.0.0",
    description="A free and open source desktop dashboard for Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Team Karmac",
    license="GPL-3.0-or-later",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "PySide6>=6.5.0",
        "requests>=2.28.0",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "karmac=main:main",
        ],
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: Qt",
        "Topic :: Desktop Environment",
        "Topic :: System :: Monitoring",
    ],
)