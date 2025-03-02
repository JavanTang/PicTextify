#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF处理模块 - 负责从PDF文件中提取文本和图片
"""

import os
import io
import logging
import PyPDF2
import pdfplumber
import fitz  # PyMuPDF
from PIL import Image

# 获取日志记录器
logger = logging.getLogger("pictextify.pdf_processor")


class PDFProcessor:
    """PDF处理类，负责从PDF文件中提取文本和图片"""

    def __init__(self, output_dir=None, text_engine="fitz", image_engine="fitz"):
        """
        初始化PDF处理器

        Args:
            output_dir (str, optional): 图片输出目录
            text_engine (str): 文本提取引擎，可选 'pypdf', 'pdfplumber' 或 'fitz'
            image_engine (str): 图片提取引擎，可选 'pdfplumber' 或 'fitz'
        """
        self.output_dir = output_dir
        self.text_engine = text_engine
        self.image_engine = image_engine
        logger.debug(
            f"初始化PDF处理器: output_dir={output_dir}, text_engine={text_engine}, image_engine={image_engine}"
        )

    def process(self, pdf_path, output_dir=None):
        """
        处理PDF文件，提取文本和图片，保持原始顺序

        Args:
            pdf_path (str): PDF文件路径
            output_dir (str, optional): 图片输出目录，如果为None则使用初始化时的目录

        Returns:
            tuple: (内容列表, 图片信息列表)
                内容列表: 每个元素为(顺序索引, 内容类型, 内容)
                    内容类型可以是 'text' 或 'image'
                    如果是 'text'，内容为文本字符串
                    如果是 'image'，内容为图片路径
                图片信息列表: 每个元素为(顺序索引, 图片路径)
        """
        # 使用传入的output_dir或初始化时的output_dir
        output_dir = output_dir or self.output_dir
        if not output_dir:
            raise ValueError("必须提供图片输出目录")

        logger.info(f"开始处理PDF文件: {pdf_path}")
        logger.debug(f"图片输出目录: {output_dir}")

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 提取有序内容
        ordered_items = []
        images_info = []
        item_index = 0

        try:
            # 使用PyMuPDF (fitz) 打开PDF文件
            doc = fitz.open(pdf_path)
            logger.info(f"PDF文件已打开，共 {doc.page_count} 页")

            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_num_display = page_num + 1  # 页码从1开始显示
                logger.debug(f"处理第 {page_num_display} 页")

                # 获取页面的所有块（包括文本和图片）
                # 使用dict格式获取，这样可以获取到更多的元数据
                page_dict = page.get_text("dict", sort=True)
                blocks = page_dict["blocks"]
                logger.debug(f"第 {page_num_display} 页提取到 {len(blocks)} 个块")

                # 处理每个块
                for block in blocks:
                    # 文本块
                    if block["type"] == 0:  # 文本块
                        text_content = ""
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text_content += span["text"] + " "

                        text_content = text_content.strip()
                        if text_content:
                            # 获取文本块的位置信息
                            pos = block["bbox"][1]  # y0坐标作为垂直位置

                            ordered_items.append((item_index, "text", text_content))
                            logger.debug(
                                f"添加有序文本: 索引={item_index}, 页码={page_num_display}, 位置={pos}, 内容长度={len(text_content)}"
                            )
                            item_index += 1

                    # 图片块
                    elif block["type"] == 1:  # 图片块
                        # 获取图片数据
                        img_bbox = block["bbox"]
                        img_pos = img_bbox[1]  # y0坐标作为垂直位置

                        # 保存图片
                        image_filename = (
                            f"page_{page_num_display}_image_{len(images_info) + 1}.png"
                        )
                        image_path = os.path.join(output_dir, image_filename)

                        # 从图片块中提取图片数据
                        try:
                            # 使用xref提取图片
                            if "image" in block:
                                pix = fitz.Pixmap(block["image"])
                                pix.save(image_path)
                                logger.debug(
                                    f"保存图片: {image_path}, 尺寸: {pix.width}x{pix.height}"
                                )
                            else:
                                # 如果没有直接的图片数据，尝试从页面截取该区域
                                clip_rect = fitz.Rect(img_bbox)
                                pix = page.get_pixmap(clip=clip_rect)
                                pix.save(image_path)
                                logger.debug(
                                    f"从页面截取图片: {image_path}, 区域: {clip_rect}"
                                )

                            ordered_items.append((item_index, "image", image_path))
                            images_info.append((item_index, image_path))
                            logger.debug(
                                f"添加有序图片: 索引={item_index}, 页码={page_num_display}, 位置={img_pos}, 路径={image_path}"
                            )
                            item_index += 1
                        except Exception as e:
                            logger.error(f"提取图片时出错: {str(e)}")

                # 如果使用dict方法没有提取到图片，尝试使用get_images方法
                if not any(block["type"] == 1 for block in blocks):
                    logger.debug(
                        f"第 {page_num_display} 页没有通过dict方法提取到图片，尝试使用get_images方法"
                    )
                    img_list = page.get_images()
                    if img_list:
                        logger.debug(
                            f"第 {page_num_display} 页通过get_images方法提取到 {len(img_list)} 张图片"
                        )

                        for img_index, img in enumerate(img_list):
                            try:
                                xref = img[0]  # 图片的xref

                                # 提取图片
                                base_image = doc.extract_image(xref)
                                image_bytes = base_image["image"]

                                # 保存图片
                                image_filename = (
                                    f"page_{page_num_display}_image_{img_index + 1}.png"
                                )
                                image_path = os.path.join(output_dir, image_filename)

                                with open(image_path, "wb") as f:
                                    f.write(image_bytes)

                                logger.debug(f"保存图片: {image_path}")

                                # 估算图片位置（使用页面高度的比例）
                                img_pos = (
                                    page.rect.height
                                    * (img_index + 1)
                                    / (len(img_list) + 1)
                                )

                                ordered_items.append((item_index, "image", image_path))
                                images_info.append((item_index, image_path))
                                logger.debug(
                                    f"添加有序图片: 索引={item_index}, 页码={page_num_display}, 位置={img_pos}, 路径={image_path}"
                                )
                                item_index += 1
                            except Exception as e:
                                logger.error(f"提取图片时出错: {str(e)}")

            # 关闭文档
            doc.close()

            logger.info(
                f"PDF处理完成: 提取了 {len(ordered_items)} 个内容项, {len(images_info)} 张图片"
            )

            # 打印内容顺序信息，帮助调试
            logger.debug("内容顺序信息:")
            for idx, content_type, content in ordered_items:
                if content_type == "text":
                    logger.debug(
                        f"  索引 {idx}: 文本, 长度={len(content)}, 前20字符: {content[:20]}..."
                    )
                else:
                    logger.debug(f"  索引 {idx}: 图片, 路径={content}")

            return ordered_items, images_info

        except Exception as e:
            logger.exception(f"处理PDF文件时出错: {str(e)}")
            raise

    def get_text_near_image(self, ordered_content, image_info):
        """
        获取图片附近的文本

        Args:
            ordered_content (list): 有序内容列表
            image_info (tuple): 图片信息(顺序索引, 图片路径)

        Returns:
            str: 图片附近的文本
        """
        image_idx = image_info[0]
        image_path = image_info[1]
        logger.debug(f"获取图片附近文本: 图片索引={image_idx}, 路径={image_path}")

        # 查找图片前后的文本
        before_text = None
        after_text = None

        # 查找图片前面的文本
        for idx, content_type, content in ordered_content:
            if idx < image_idx and content_type == "text":
                before_text = content
                logger.debug(f"找到图片前文本: 索引={idx}, 长度={len(content)}")
            elif idx > image_idx and content_type == "text" and after_text is None:
                after_text = content
                logger.debug(f"找到图片后文本: 索引={idx}, 长度={len(content)}")
                break

        # 组合前后文本
        nearby_text = []
        if before_text:
            nearby_text.append(before_text)
        if after_text:
            nearby_text.append(after_text)

        result = "\n".join(nearby_text)
        logger.debug(f"图片附近文本长度: {len(result)}")
        return result
