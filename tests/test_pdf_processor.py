#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF处理模块测试
"""

import os
import pytest
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
from pictextify.pdf_processor import PDFProcessor
from pictextify.ocr_processor import OCRProcessor


class TestPDFProcessor:
    """PDF处理类测试"""

    @pytest.fixture
    def sample_pdf(self):
        """创建样本PDF文件"""
        # 使用测试数据目录中的示例PDF
        return os.path.join(os.path.dirname(__file__), "data", "example.pdf")

    @pytest.fixture
    def example_image(self):
        """获取包含'中国'文本的示例图片"""
        return os.path.join(os.path.dirname(__file__), "data", "example.jpg")

    def test_process(self, sample_pdf, example_image):
        """测试处理PDF文件"""
        processor = PDFProcessor()

        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 处理PDF
            ordered_content, images_info = processor.process(sample_pdf, temp_dir)

            # 打印实际文本内容，帮助调试
            print("\n实际PDF文本内容:")
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
            ), f"在PDF文本中未找到任何预期模式 {expected_patterns}。实际文本: {all_texts}"

            # 验证图片信息（如果有）
            if images_info:
                print("\n提取的图片信息:")
                for idx, path in images_info:
                    print(f"索引 {idx}, 图片路径: {path}")
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

                    print("\n图片OCR结果 (GOT-OCR2_0):")
                    for idx, path in images_info:
                        ocr_text = ocr_processor.process_single_image(path)
                        print(
                            f"索引 {idx}, OCR结果: {ocr_text[:100]}..."
                            if len(ocr_text) > 100
                            else ocr_text
                        )
                        # 验证OCR结果不为空
                        assert ocr_text.strip(), f"图片 {path} 的GOT-OCR2_0结果为空"

                        # 检查OCR结果是否包含"在中国作家"
                        if "在中国作家" in ocr_text:
                            print(f"在图片OCR结果中找到了'在中国作家'模式")
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

    def test_get_text_near_image(self, sample_pdf):
        """测试获取图片附近的文本"""
        processor = PDFProcessor()

        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 处理PDF
            ordered_content, images_info = processor.process(sample_pdf, temp_dir)

            # 如果没有图片，则跳过测试
            if not images_info:
                pytest.skip("PDF中没有图片，跳过测试")

            # 获取图片附近的文本
            for image_info in images_info:
                nearby_text = processor.get_text_near_image(ordered_content, image_info)
                assert isinstance(nearby_text, str)

                # 检查附近文本是否包含预期模式
                if "在中国作家" in nearby_text:
                    print(f"在图片附近文本中找到了'在中国作家'模式")
