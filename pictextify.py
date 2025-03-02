#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PicTextify - 一个从文档中提取文本和图片，并进行OCR识别的工具
"""

import os
import argparse
import tempfile
import logging
from pictextify import setup_logger, extract_from_file
from pictextify.pdf_processor import PDFProcessor
from pictextify.docx_processor import DocxProcessor
from pictextify.ocr_processor import OCRProcessor
from pictextify.text_merger import TextMerger

# 获取日志记录器
logger = logging.getLogger("pictextify.main")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="从文档中提取文本和图片，并进行OCR识别"
    )
    parser.add_argument("--input", "-i", required=True, help="输入文件路径")
    parser.add_argument("--output", "-o", required=True, help="输出文件路径")
    parser.add_argument("--lang", "-l", default=None, help="OCR语言")
    parser.add_argument(
        "--model", "-m", default=None, help="OCR模型路径，默认使用GOT-OCR2_0"
    )
    parser.add_argument(
        "--engine", "-e", default="got-ocr", help="OCR引擎，默认为got-ocr"
    )
    parser.add_argument(
        "--device", "-d", default="cpu", help="计算设备，可选 'cpu' 或 'cuda'"
    )
    parser.add_argument(
        "--debug", action="store_true", help="启用调试模式，输出更详细的日志"
    )
    args = parser.parse_args()

    # 设置日志
    setup_logger(args.debug)
    logger.info("PicTextify 启动")
    logger.info(f"输入文件: {args.input}")
    logger.info(f"输出文件: {args.output}")
    logger.debug(f"OCR语言: {args.lang}")
    logger.debug(f"OCR模型: {args.model}")
    logger.debug(f"OCR引擎: {args.engine}")
    logger.debug(f"计算设备: {args.device}")
    logger.debug(f"调试模式: {args.debug}")

    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        logger.error(f"输入文件不存在: {args.input}")
        print(f"错误: 输入文件 '{args.input}' 不存在")
        return

    # 创建临时目录用于存储提取的图片
    temp_dir = tempfile.mkdtemp()
    logger.debug(f"创建临时目录: {temp_dir}")

    try:
        # 根据文件类型选择处理器
        file_ext = os.path.splitext(args.input)[1].lower()
        logger.info(f"文件类型: {file_ext}")

        # 创建OCR处理器
        logger.info("创建OCR处理器")
        ocr_processor = OCRProcessor(
            lang=args.lang,
            model_path=args.model,
            engine=args.engine,
            device=args.device,
        )

        # 创建文本合并器
        logger.info("创建文本合并器")
        text_merger = TextMerger()

        # 处理文件
        logger.info("开始处理文件")
        all_content = []  # 存储所有内容，包括文本和OCR结果

        if file_ext == ".pdf":
            logger.info("使用PDF处理器")
            processor = PDFProcessor(temp_dir)
            ordered_content, images_info = processor.process(args.input)

            # 将文本内容添加到all_content
            for idx, content_type, content in ordered_content:
                logger.debug(
                    f"添加文本内容: 索引={idx}, 类型={content_type}, 长度={len(content)}"
                )
                all_content.append((idx, content_type, content))

            # 处理图片并添加OCR结果
            if images_info:
                logger.info(f"处理 {len(images_info)} 张图片")
                ocr_results = ocr_processor.process_images(images_info)

                # 将OCR结果添加到all_content
                for idx, ocr_text in ocr_results:
                    logger.debug(f"添加OCR结果: 索引={idx}, 长度={len(ocr_text)}")
                    all_content.append((idx, "ocr", ocr_text))
            else:
                logger.info("没有图片需要处理")

        elif file_ext in [".docx", ".doc"]:
            logger.info("使用Word处理器")
            processor = DocxProcessor(temp_dir)
            ordered_content, images_info = processor.process(args.input)

            # 将文本内容添加到all_content
            for idx, content_type, content in ordered_content:
                logger.debug(
                    f"添加文本内容: 索引={idx}, 类型={content_type}, 长度={len(content)}"
                )
                all_content.append((idx, content_type, content))

            # 处理图片并添加OCR结果
            if images_info:
                logger.info(f"处理 {len(images_info)} 张图片")
                ocr_results = ocr_processor.process_images(images_info)

                # 将OCR结果添加到all_content
                for idx, ocr_text in ocr_results:
                    logger.debug(f"添加OCR结果: 索引={idx}, 长度={len(ocr_text)}")
                    all_content.append((idx, "ocr", ocr_text))
            else:
                logger.info("没有图片需要处理")

        else:
            logger.error(f"不支持的文件类型: {file_ext}")
            print(f"错误: 不支持的文件类型 '{file_ext}'")
            return

        # 按索引排序所有内容
        logger.info("对所有内容按索引排序")
        all_content.sort(key=lambda x: x[0])
        logger.debug(f"排序后的内容数量: {len(all_content)}")

        # 合并文本
        logger.info("合并文本")
        merged_text = text_merger.merge(all_content)
        logger.debug(f"合并后的文本长度: {len(merged_text)}")

        # 写入输出文件
        logger.info(f"写入输出文件: {args.output}")
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(merged_text)

        logger.info("处理完成")
        print(f"处理完成，结果已保存到 '{args.output}'")

    except Exception as e:
        logger.exception(f"处理文件时出错: {str(e)}")
        print(f"错误: {str(e)}")
    finally:
        # 清理临时目录
        import shutil

        logger.debug(f"清理临时目录: {temp_dir}")
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
