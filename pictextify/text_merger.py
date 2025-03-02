#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文本合并模块 - 负责将提取的文本和OCR结果合并
"""

import logging

# 获取日志记录器
logger = logging.getLogger("pictextify.text_merger")


class TextMerger:
    """文本合并类，负责将提取的文本和OCR结果合并"""

    def __init__(self):
        """初始化文本合并器"""
        logger.debug("初始化文本合并器")

    def merge(self, content_items):
        """
        合并文本和OCR结果

        Args:
            content_items (list): 内容项列表，每个元素为(位置索引, 内容类型, 内容)

        Returns:
            str: 合并后的文本
        """
        logger.info(f"开始合并 {len(content_items)} 个内容项")

        # 检查输入格式
        if not content_items:
            logger.warning("没有内容需要合并")
            return ""

        # 记录内容项的类型分布
        content_types = {}
        for _, content_type, _ in content_items:
            content_types[content_type] = content_types.get(content_type, 0) + 1
        logger.debug(f"内容类型分布: {content_types}")

        # 按位置索引排序
        logger.debug("按位置索引排序内容项")
        sorted_items = sorted(content_items, key=lambda x: x[0])

        # 创建OCR结果映射，用于替换图片路径
        ocr_map = {}
        for idx, content_type, content in sorted_items:
            if content_type == "ocr" and content and content.strip():
                # 找到对应的图片索引
                for img_idx, img_type, img_path in sorted_items:
                    if img_type == "image" and img_idx == idx:
                        ocr_map[img_path] = content
                        logger.debug(
                            f"创建OCR映射: 图片路径={img_path}, OCR文本长度={len(content)}"
                        )
                        break

        # 合并文本
        merged_text = []
        for idx, content_type, content in sorted_items:
            if content_type == "text" and content and content.strip():
                logger.debug(f"添加文本内容: 索引={idx}, 长度={len(content)}")
                merged_text.append(content)
            elif content_type == "image" and content in ocr_map:
                # 使用OCR结果替换图片路径
                logger.debug(
                    f"使用OCR结果替换图片路径: 索引={idx}, OCR文本长度={len(ocr_map[content])}"
                )
                merged_text.append(ocr_map[content])
            elif content_type == "image":
                # 如果没有OCR结果，添加图片说明
                logger.debug(f"图片没有OCR结果: 索引={idx}, 路径={content}")
                merged_text.append(f"[图片内容无法识别]")
            elif content_type == "ocr":
                # OCR结果已经通过映射添加，这里跳过
                logger.debug(f"跳过单独的OCR内容: 索引={idx}, 长度={len(content)}")
                continue
            else:
                logger.debug(f"跳过空内容项: 索引={idx}, 类型={content_type}")

        # 使用换行符连接所有文本
        result = "\n\n".join(merged_text)
        logger.info(f"合并完成，最终文本长度: {len(result)}")
        return result

    def merge_with_metadata(self, ordered_content):
        """
        合并有序内容，并保留元数据

        Args:
            ordered_content (list): 有序内容列表，每个元素为(顺序索引, 内容类型, 内容)

        Returns:
            str: 合并后的文本，包含元数据
        """
        # 按顺序索引排序
        ordered_content.sort(key=lambda x: x[0])

        # 合并为一个字符串，每个内容块之间用分隔符分隔
        merged_text = []
        for position, content_type, content in ordered_content:
            if content_type == "text":
                merged_text.append(f"--- 文本 (位置: {position}) ---\n{content}")
            elif content_type == "image":
                merged_text.append(f"--- 图片 (位置: {position}, 路径: {content}) ---")

        return "\n\n".join(merged_text)

    def align_pattern(self, ordered_content, patterns=None):
        """
        对齐内容中的特定模式，并按照模式组织内容

        Args:
            ordered_content (list): 有序内容列表，每个元素为(顺序索引, 内容类型, 内容)
            patterns (list, optional): 要识别的模式列表，如["标题", "正文", "图片说明"]

        Returns:
            str: 按模式对齐的文本
        """
        logger.info(f"开始按模式对齐 {len(ordered_content)} 个内容项")

        # 默认模式分类
        if patterns is None:
            patterns = ["标题", "正文", "图片说明"]
            logger.debug(f"使用默认模式分类: {patterns}")
        else:
            logger.debug(f"使用自定义模式分类: {patterns}")

        # 按顺序索引排序
        logger.debug("按位置索引排序内容项")
        sorted_items = sorted(ordered_content, key=lambda x: x[0])

        # 分类内容
        categorized_content = {pattern: [] for pattern in patterns}
        categorized_content["其他"] = []  # 未分类内容

        # 尝试对内容进行分类
        for idx, content_type, content in sorted_items:
            if not content or not content.strip():
                logger.debug(f"跳过空内容项: 索引={idx}, 类型={content_type}")
                continue

            # 根据内容特征进行分类
            if content_type == "text":
                # 简单的启发式分类
                if len(content) < 100 and content.strip().endswith(
                    ("。", ".", "!", "?")
                ):
                    # 可能是标题或短句
                    categorized_content["标题"].append((idx, content))
                    logger.debug(f"将内容 {idx} 分类为'标题', 长度={len(content)}")
                elif "图" in content and len(content) < 200:
                    # 可能是图片说明
                    categorized_content["图片说明"].append((idx, content))
                    logger.debug(f"将内容 {idx} 分类为'图片说明', 长度={len(content)}")
                else:
                    # 默认为正文
                    categorized_content["正文"].append((idx, content))
                    logger.debug(f"将内容 {idx} 分类为'正文', 长度={len(content)}")
            elif content_type == "image" or content_type == "ocr":
                # OCR结果通常与图片相关
                if content_type == "ocr":
                    categorized_content["图片说明"].append((idx, content))
                    logger.debug(
                        f"将OCR内容 {idx} 分类为'图片说明', 长度={len(content)}"
                    )
                else:
                    categorized_content["其他"].append((idx, f"[图片: {content}]"))
                    logger.debug(f"将图片 {idx} 分类为'其他'")
            else:
                categorized_content["其他"].append((idx, content))
                logger.debug(f"将内容 {idx} 分类为'其他', 类型={content_type}")

        # 格式化结果
        result = []

        # 添加标题部分
        if categorized_content["标题"]:
            result.append("# 标题")
            for _, content in sorted(categorized_content["标题"], key=lambda x: x[0]):
                result.append(content)
            result.append("")

        # 添加正文部分
        if categorized_content["正文"]:
            result.append("# 正文")
            for _, content in sorted(categorized_content["正文"], key=lambda x: x[0]):
                result.append(content)
            result.append("")

        # 添加图片说明部分
        if categorized_content["图片说明"]:
            result.append("# 图片说明")
            for _, content in sorted(
                categorized_content["图片说明"], key=lambda x: x[0]
            ):
                result.append(content)
            result.append("")

        # 添加其他内容
        if categorized_content["其他"]:
            result.append("# 其他内容")
            for _, content in sorted(categorized_content["其他"], key=lambda x: x[0]):
                result.append(content)

        formatted_result = "\n\n".join(result)
        logger.info(f"模式对齐完成，最终文本长度: {len(formatted_result)}")
        return formatted_result
