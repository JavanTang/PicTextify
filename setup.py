#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取README.md文件内容
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements.txt文件内容
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [
        line.strip()
        for line in f.readlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="pictextify",
    version="0.1.0",
    author="TangZhifeng",
    author_email="tzfjobmail@gmail.com",
    description="从PDF和Word文档中提取文本和图片，并进行OCR处理",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JavanTang/PicTextify",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pictextify=pictextify.cli:main",
        ],
    },
)
