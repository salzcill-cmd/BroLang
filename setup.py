"""
Setup untuk BroLang
===================

Konfigurasi instalasi dan distribusi BroLang.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="brolang",
    version="2.0.0",
    description="BroLang - Bahasa Pemrograman Edukatif Profesional",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="BroLang Team",
    author_email="team@brolang.dev",
    url="https://github.com/brolang/brolang",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bro=brolang.cli:main",
            "bropm=brolang.package_manager.manager:main",
            "bro-lsp=brolang.lsp.server:start_lsp",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Education",
    ],
)
