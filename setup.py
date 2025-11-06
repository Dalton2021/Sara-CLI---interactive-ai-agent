"""Setup script for Sara AI Terminal Agent"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sara-ai-agent",
    version="0.1.0",
    author="Your Name",
    description="Sara - AI Terminal Agent for Code Assistance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "openai>=1.0.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "sara=sara.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
