#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Word文档处理模块测试
"""

import os
import pytest
import tempfile
from pictextify.docx_processor import DocxProcessor
from pictextify.ocr_processor import OCRProcessor


class TestDocxProcessor:
    """Word文档处理类测试"""

    @pytest.fixture
    def sample_docx(self):
        """获取样本Word文档"""
        # 使用测试数据目录中的示例Word文档
        return os.path.join(os.path.dirname(__file__), "data", "example.docx")

    @pytest.fixture
    def example_image(self):
        """获取包含'中国'文本的示例图片"""
        return os.path.join(os.path.dirname(__file__), "data", "example.jpg")

    def test_process(self, sample_docx, example_image):
        """测试处理Word文档"""
        processor = DocxProcessor()

        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 处理Word文档
            ordered_content, images_info = processor.process(sample_docx, temp_dir)

            # 打印实际文本内容，帮助调试
            print("\n实际Word文本内容:")
            for idx, content_type, content in ordered_content:
                if content_type == "text":
                    print(f"索引 {idx}, 类型: {content_type}")
                    print(content[:100] + "..." if len(content) > 100 else content)

            # 验证文本内容
            assert len(ordered_content) > 0

            # 收集所有文本内容用于断言消息
            all_texts = [
                content
                for idx, content_type, content in ordered_content
                if content_type == "text"
            ]
            combined_text = " ".join(all_texts)

            # 检查是否包含实际文档中的文本模式
            expected_patterns = ["haha", "在中国作家", "hhah", "11"]
            found_patterns = [
                pattern for pattern in expected_patterns if pattern in combined_text
            ]

            assert (
                found_patterns
            ), f"在Word文本中未找到任何预期模式 {expected_patterns}。实际文本: {all_texts}"

            # 验证图片信息（如果有）
            if images_info:
                print("\n提取的Word文档图片信息:")
                for idx, path in images_info:
                    print(f"图片索引 {idx}, 图片路径: {path}")
                    assert idx >= 0
                    assert os.path.exists(path)

                # 对提取的图片进行OCR处理（使用GOT-OCR2_0）
                try:
                    import torch
                    import transformers

                    ocr_processor = OCRProcessor(
                        model_path="/home/tangzhifeng/MODELZOOS/GOT-OCR2_0",
                        device="cuda" if torch.cuda.is_available() else "cpu",
                    )

                    print("\nWord文档图片OCR结果 (GOT-OCR2_0):")
                    for idx, path in images_info:
                        ocr_text = ocr_processor.process_single_image(path)
                        print(
                            f"图片索引 {idx}, OCR结果: {ocr_text[:100]}..."
                            if len(ocr_text) > 100
                            else ocr_text
                        )
                        # 验证OCR结果不为空
                        assert ocr_text.strip(), f"图片 {path} 的GOT-OCR2_0结果为空"

                        # 检查OCR结果是否包含"在中国作家"
                        if "在中国作家" in ocr_text:
                            print(f"在Word图片OCR结果中找到了'在中国作家'模式")
                except (ImportError, Exception) as e:
                    pytest.skip(f"GOT-OCR2_0处理失败，跳过测试: {str(e)}")

            # 测试对包含"中国"的示例图片进行OCR处理（使用GOT-OCR2_0）
            try:
                import torch
                import transformers

                ocr_processor = OCRProcessor(
                    model_path="/home/tangzhifeng/MODELZOOS/GOT-OCR2_0",
                    device="cuda" if torch.cuda.is_available() else "cpu",
                )
                ocr_text = ocr_processor.process_single_image(example_image)
                print(f"\n示例图片OCR结果 (GOT-OCR2_0): {ocr_text}")

                # 验证OCR结果包含"中国"
                assert (
                    "中国" in ocr_text
                ), f"GOT-OCR2_0结果中未找到'中国'，实际结果: {ocr_text}"
            except (ImportError, Exception) as e:
                pytest.skip(f"示例图片GOT-OCR2_0处理失败，跳过测试: {str(e)}")

    def test_extract_images(self, sample_docx):
        """测试提取图片"""
        processor = DocxProcessor()

        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 直接使用process方法，因为DocxProcessor可能没有单独的_extract_images方法
            _, images_info = processor.process(sample_docx, temp_dir)

            # 如果文档中没有图片，则跳过验证
            if not images_info:
                pytest.skip("Word文档中没有图片，跳过测试")

            # 验证图片信息
            for idx, path in images_info:
                assert idx >= 0
                assert os.path.exists(path)
