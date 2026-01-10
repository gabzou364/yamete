#!/usr/bin/env python3
"""Setup script for yamete Python CLI."""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="yamete",
    version="2.0.0",
    description="Yamete - Manga/Hentai downloader in Python CLI",
    author="Jay MOULIN",
    author_email="jaymoulin@gmail.com",
    license="MIT",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "yamete=yamete.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
