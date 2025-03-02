#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PicTextify CLI - 命令行接口
"""

import argparse
import sys
import logging
from . import extract_from_file, extract_and_align_pattern, __version__, setup_logger
from .ocr_processor import OCRProcessor


def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(
        description="从PDF和Word文档中提取文本和图片，并进行OCR处理"
    )
    parser.add_argument(
        "--input", "-i", required=True, help="输入文件路径(PDF或DOCX格式)"
    )
    parser.add_argument(
        "--output", "-o", help="输出文本文件路径(默认为input文件名.txt)"
    )
    parser.add_argument(
        "--ocr-model",
        help="GOT-OCR2_0模型路径(默认为/home/tangzhifeng/MODELZOOS/GOT-OCR2_0)",
    )
    parser.add_argument(
        "--device", choices=["cpu", "cuda"], default="cuda", help="计算设备(默认为cuda)"
    )
    parser.add_argument(
        "--align-pattern",
        action="store_true",
        help="按特定模式对齐内容(如'haha'、'在中国作家...'等)",
    )
    parser.add_argument("--list-models", action="store_true", help="列出推荐的OCR模型")
    parser.add_argument(
        "--version", "-v", action="version", version=f"PicTextify {__version__}"
    )
    # 添加debug参数
    parser.add_argument(
        "--debug", action="store_true", help="启用调试模式，输出更详细的日志"
    )
    # 添加OCR引擎参数
    parser.add_argument(
        "--ocr-engine", default="got-ocr", help="OCR引擎，默认为got-ocr"
    )
    # 添加语言参数
    parser.add_argument("--lang", default=None, help="OCR语言")

    args = parser.parse_args()

    # 设置日志
    setup_logger(args.debug)
    logger = logging.getLogger("pictextify")

    # 列出推荐的OCR模型
    if args.list_models:
        print("推荐的OCR模型:")
        for model in OCRProcessor.list_huggingface_models():
            print(f"  - {model}")
        return 0

    # 设置默认输出文件名
    if not args.output:
        import os

        base_name = os.path.splitext(args.input)[0]
        args.output = f"{base_name}.txt"

    try:
        # 处理文件
        if args.align_pattern:
            # 使用模式对齐功能
            extract_and_align_pattern(
                args.input,
                args.output,
                ocr_model=args.ocr_model,
                device=args.device,
                ocr_engine=args.ocr_engine,
                lang=args.lang,
            )
            print(f"处理完成! 已按模式对齐内容，输出文件: {args.output}")
        else:
            # 使用标准提取功能
            extract_from_file(
                args.input,
                args.output,
                ocr_model=args.ocr_model,
                device=args.device,
                ocr_engine=args.ocr_engine,
                lang=args.lang,
            )
            print(f"处理完成! 输出文件: {args.output}")
        return 0
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
