#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PicTextify - 从PDF和Word文档中提取文本和图片，并进行OCR处理
"""

import os
import tempfile
import logging
from typing import Optional, Tuple, List, Dict, Any, Union


# 配置日志
def setup_logger(debug_mode=False):
    """
    设置日志配置

    Args:
        debug_mode (bool): 是否启用调试模式，True则输出DEBUG级别日志，False则输出INFO级别
    """
    log_level = logging.DEBUG if debug_mode else logging.INFO

    # 检查环境变量是否设置了调试模式
    if os.environ.get("PICTEXTIFY_DEBUG", "").lower() in ("1", "true", "yes"):
        log_level = logging.DEBUG

    # 配置根日志
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 获取并返回pictextify日志器
    logger = logging.getLogger("pictextify")
    logger.setLevel(log_level)

    # 如果已经有处理器，不再添加新的处理器
    if not logger.handlers:
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# 初始化日志器
logger = setup_logger(debug_mode=False)

from .file_handler import FileHandler
from .pdf_processor import PDFProcessor
from .docx_processor import DocxProcessor
from .ocr_processor import OCRProcessor
from .text_merger import TextMerger

__version__ = "0.1.0"
__all__ = [
    "FileHandler",
    "PDFProcessor",
    "DocxProcessor",
    "OCRProcessor",
    "TextMerger",
    "extract_from_file",
    "extract_and_align_pattern",
    "setup_logger",  # 添加日志设置函数到公开API
]


def extract_from_file(
    file_path,
    output_file=None,
    ocr_model=None,
    device="cuda",
    debug_mode=False,
    ocr_engine="got-ocr",
    lang=None,
):
    """
    从文件中提取文本和图片，并进行OCR处理

    Args:
        file_path (str): 输入文件路径(PDF或DOCX格式)
        output_file (str, optional): 输出文本文件路径，如果为None则不输出到文件
        ocr_model (str, optional): GOT-OCR2_0模型路径，默认为/home/tangzhifeng/MODELZOOS/GOT-OCR2_0
        device (str, optional): 计算设备，可选 'cpu' 或 'cuda'，默认为'cuda'
        debug_mode (bool, optional): 是否启用调试模式，默认为False
        ocr_engine (str, optional): OCR引擎，默认为'got-ocr'
        lang (str, optional): OCR语言，默认为None

    Returns:
        str: 提取的文本内容
    """
    import os
    import tempfile
    import shutil

    # 设置日志级别
    logger = setup_logger(debug_mode=debug_mode)
    logger.debug(f"开始处理文件: {file_path}")

    # 检查输入文件是否存在
    if not os.path.exists(file_path):
        logger.error(f"输入文件不存在: {file_path}")
        raise FileNotFoundError(f"输入文件 '{file_path}' 不存在")

    # 创建临时目录用于存储提取的图片
    temp_dir = tempfile.mkdtemp()
    logger.debug(f"创建临时目录: {temp_dir}")

    try:
        # 处理文件
        file_handler = FileHandler()
        file_type = file_handler.get_file_type(file_path)
        logger.info(f"检测到文件类型: {file_type}")

        if file_type == "pdf":
            logger.debug("使用PDF处理器")
            processor = PDFProcessor()
            ordered_content, images_info = processor.process(file_path, temp_dir)
        elif file_type == "docx":
            logger.debug("使用Word处理器")
            processor = DocxProcessor()
            ordered_content, images_info = processor.process(file_path, temp_dir)
        else:
            logger.error(f"不支持的文件类型: {file_type}")
            raise ValueError(f"不支持的文件类型 '{file_type}'，仅支持PDF和DOCX格式")

        logger.info(
            f"提取内容: {len(ordered_content)} 项内容, {len(images_info)} 张图片"
        )
        logger.debug(f"图片信息: {images_info}")

        # OCR处理图片
        logger.debug(
            f"初始化OCR处理器, 模型: {ocr_model}, 设备: {device}, 引擎: {ocr_engine}, 语言: {lang}"
        )
        ocr_processor = OCRProcessor(
            model_path=ocr_model, device=device, engine=ocr_engine, lang=lang
        )

        # 处理图片并将OCR结果添加到有序内容中
        for idx, image_path in images_info:
            logger.debug(f"处理图片 {idx}: {image_path}")
            ocr_text = ocr_processor.process_single_image(image_path)
            if ocr_text and ocr_text.strip():
                logger.debug(f"图片 {idx} OCR结果: {ocr_text[:100]}...")
                # 在图片后面添加OCR结果
                ordered_content.append((idx + 0.5, "text", ocr_text))
            else:
                logger.warning(f"图片 {idx} OCR结果为空")

        # 重新排序内容
        ordered_content.sort(key=lambda x: x[0])
        logger.debug("内容已排序")

        # 合并文本
        logger.debug("开始合并文本")
        text_merger = TextMerger()
        final_text = text_merger.merge(ordered_content)
        logger.debug(f"合并完成, 文本长度: {len(final_text)}")

        # 如果指定了输出文件，则写入
        if output_file:
            logger.info(f"写入输出文件: {output_file}")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(final_text)

        return final_text

    except Exception as e:
        logger.exception(f"处理文件时出错: {str(e)}")
        raise
    finally:
        # 清理临时目录
        logger.debug(f"清理临时目录: {temp_dir}")
        shutil.rmtree(temp_dir)


def extract_and_align_pattern(
    file_path,
    output_file=None,
    ocr_model=None,
    device="cuda",
    debug_mode=False,
    ocr_engine="got-ocr",
    lang=None,
):
    """
    从文件中提取文本和图片，进行OCR处理，并按特定模式对齐内容

    Args:
        file_path (str): 输入文件路径(PDF或DOCX格式)
        output_file (str, optional): 输出文本文件路径，如果为None则不输出到文件
        ocr_model (str, optional): GOT-OCR2_0模型路径，默认为/home/tangzhifeng/MODELZOOS/GOT-OCR2_0
        device (str, optional): 计算设备，可选 'cpu' 或 'cuda'，默认为'cuda'
        debug_mode (bool, optional): 是否启用调试模式，默认为False
        ocr_engine (str, optional): OCR引擎，默认为'got-ocr'
        lang (str, optional): OCR语言，默认为None

    Returns:
        str: 按模式对齐的文本内容
    """
    import os
    import tempfile
    import shutil

    # 设置日志级别
    logger = setup_logger(debug_mode=debug_mode)
    logger.debug(f"开始处理文件并对齐模式: {file_path}")

    # 检查输入文件是否存在
    if not os.path.exists(file_path):
        logger.error(f"输入文件不存在: {file_path}")
        raise FileNotFoundError(f"输入文件 '{file_path}' 不存在")

    # 创建临时目录用于存储提取的图片
    temp_dir = tempfile.mkdtemp()
    logger.debug(f"创建临时目录: {temp_dir}")

    try:
        # 处理文件
        file_handler = FileHandler()
        file_type = file_handler.get_file_type(file_path)
        logger.info(f"检测到文件类型: {file_type}")

        if file_type == "pdf":
            logger.debug("使用PDF处理器")
            processor = PDFProcessor()
            ordered_content, images_info = processor.process(file_path, temp_dir)
        elif file_type == "docx":
            logger.debug("使用Word处理器")
            processor = DocxProcessor()
            ordered_content, images_info = processor.process(file_path, temp_dir)
        else:
            logger.error(f"不支持的文件类型: {file_type}")
            raise ValueError(f"不支持的文件类型 '{file_type}'，仅支持PDF和DOCX格式")

        logger.info(
            f"提取内容: {len(ordered_content)} 项内容, {len(images_info)} 张图片"
        )
        logger.debug(f"图片信息: {images_info}")

        # OCR处理图片
        logger.debug(
            f"初始化OCR处理器, 模型: {ocr_model}, 设备: {device}, 引擎: {ocr_engine}, 语言: {lang}"
        )
        ocr_processor = OCRProcessor(
            model_path=ocr_model, device=device, engine=ocr_engine, lang=lang
        )

        # 处理图片并将OCR结果添加到有序内容中
        for idx, image_path in images_info:
            logger.debug(f"处理图片 {idx}: {image_path}")
            ocr_text = ocr_processor.process_single_image(image_path)
            if ocr_text and ocr_text.strip():
                logger.debug(f"图片 {idx} OCR结果: {ocr_text[:100]}...")
                # 在图片后面添加OCR结果
                ordered_content.append((idx + 0.5, "text", ocr_text))
            else:
                logger.warning(f"图片 {idx} OCR结果为空")

        # 重新排序内容
        ordered_content.sort(key=lambda x: x[0])
        logger.debug("内容已排序")

        # 使用模式对齐功能合并文本
        logger.debug("开始按模式对齐文本")
        text_merger = TextMerger()
        aligned_text = text_merger.align_pattern(ordered_content)
        logger.debug(f"对齐完成, 文本长度: {len(aligned_text)}")

        # 如果指定了输出文件，则写入
        if output_file:
            logger.info(f"写入输出文件: {output_file}")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(aligned_text)

        return aligned_text

    except Exception as e:
        logger.exception(f"处理文件时出错: {str(e)}")
        raise
    finally:
        # 清理临时目录
        logger.debug(f"清理临时目录: {temp_dir}")
        shutil.rmtree(temp_dir)
