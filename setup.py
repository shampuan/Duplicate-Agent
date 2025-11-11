#!/usr/bin/env python3
"""
Duplicate Agent - Duplicate Files Finder and Cleaner
Setup configuration
"""

from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

VERSION = "0.9.1"

setup(
    name="duplicate-agent",
    version=VERSION,
    author="A. Serhat KILIÇOĞLU (shampuan)",
    author_email="",
    description="A powerful duplicate file finder and cleaner with GUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shampuan/Duplicate-Agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PySide6>=6.5.0",
        "watchdog>=3.0.0",
        "schedule>=1.2.0",
        "pillow>=10.0.0",
        "imagehash>=4.3.1",
    ],
    entry_points={
        "console_scripts": [
            "duplicate-agent=duplicateagent0.9.1:main",
        ],
        "gui_scripts": [
            "duplicate-agent-gui=duplicateagent0.9.1:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["languages/*.ini", "*.png", "*.ico"],
    },
    keywords="duplicate files finder cleaner deduplication disk-space",
    project_urls={
        "Bug Reports": "https://github.com/shampuan/Duplicate-Agent/issues",
        "Source": "https://github.com/shampuan/Duplicate-Agent",
    },
)
