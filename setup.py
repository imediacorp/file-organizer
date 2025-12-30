"""
Setup script for file-organizer package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README if it exists
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="file-organizer",
    version="1.0.0",
    description="A flexible, extensible tool for organizing large content trees",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/file-organizer",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=5.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "file-organizer=file_organizer.cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities",
    ],
)

