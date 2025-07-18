#!/usr/bin/env python3
"""
Setup script for GenCoMo (GENeral-morphology COmpartmental MOdeling)
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gencomo",
    version="0.1.0",
    author="Jordan Fox",
    author_email="jmrfox@example.com",
    description="GENeral-morphology COmpartmental MOdeling for complex neuronal simulations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jmrfox/gencomo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Biology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },
    entry_points={
        # Note: CLI disabled since it depends on modules moved to dev_storage
        # "console_scripts": [
        #     "gencomo=gencomo.cli:main",
        # ],
    },
)
