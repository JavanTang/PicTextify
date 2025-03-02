#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pictextify",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="从PDF和Word文档中提取文本和图片，并进行OCR处理",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/PicTextify",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "PyPDF2>=3.0.0",
        "pdfplumber>=0.10.0",
        "python-docx>=0.8.10",
        "pytesseract>=0.3.8",
        "Pillow>=9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "pictextify=pictextify.cli:main",
        ],
    },
) 