#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OCR处理模块测试
"""

import os
import pytest
from PIL import Image, ImageDraw, ImageFont
from pictextify.ocr_processor import OCRProcessor


class TestOCRProcessor:
    """OCR处理类测试"""

    @pytest.fixture
    def sample_image(self, tmp_path):
        """创建包含文本的样本图片"""
        # 创建一个白色背景的图片
        image = Image.new("RGB", (300, 100), color="white")
        draw = ImageDraw.Draw(image)

        # 尝试加载字体，如果失败则使用默认字体
        try:
            font = ImageFont.truetype("Arial", 24)
        except IOError:
            font = ImageFont.load_default()

        # 在图片上绘制文本
        draw.text((10, 10), "Hello, World!", fill="black", font=font)

        # 保存图片
        image_path = os.path.join(tmp_path, "sample_text.png")
        image.save(image_path)

        return image_path

    @pytest.fixture
    def example_image(self):
        """获取包含'中国'文本的示例图片"""
        return os.path.join(os.path.dirname(__file__), "data", "example.jpg")

    def test_got_ocr(self, sample_image):
        """测试GOT-OCR2_0引擎"""
        # 跳过测试如果没有安装transformers
        try:
            import transformers
            import torch
        except ImportError:
            pytest.skip("Transformers库不可用")

        # 尝试加载GOT-OCR2_0模型
        try:
            processor = OCRProcessor(
                model_path="/home/tangzhifeng/MODELZOOS/GOT-OCR2_0",
                device="cuda" if torch.cuda.is_available() else "cpu",
            )
        except Exception as e:
            pytest.skip(f"无法加载GOT-OCR2_0模型: {str(e)}")

        # 处理图片
        text = processor.process_single_image(sample_image)

        # 打印OCR结果，帮助调试
        print(f"\nGOT-OCR2_0结果: {text}")

        # 验证结果
        assert text.strip()

    def test_got_ocr_chinese(self, example_image):
        """测试GOT-OCR2_0引擎识别中文"""
        # 跳过测试如果没有安装transformers
        try:
            import transformers
            import torch
        except ImportError:
            pytest.skip("Transformers库不可用")

        # 尝试加载GOT-OCR2_0模型
        try:
            processor = OCRProcessor(
                model_path="/home/tangzhifeng/MODELZOOS/GOT-OCR2_0",
                device="cuda" if torch.cuda.is_available() else "cpu",
            )
        except Exception as e:
            pytest.skip(f"无法加载GOT-OCR2_0模型: {str(e)}")

        # 处理图片
        text = processor.process_single_image(example_image)

        # 打印OCR结果，帮助调试
        print(f"\nGOT-OCR2_0中文结果: {text}")

        # 验证结果
        assert text.strip()
        # 检查是否包含"中国"
        assert "中国" in text, f"GOT-OCR2_0结果中未找到'中国'，实际结果: {text}"

    def test_process_images(self, sample_image):
        """测试批量处理图片"""
        # 跳过测试如果没有安装transformers
        try:
            import transformers
            import torch
        except ImportError:
            pytest.skip("Transformers库不可用")

        # 尝试加载GOT-OCR2_0模型
        try:
            processor = OCRProcessor(
                model_path="/home/tangzhifeng/MODELZOOS/GOT-OCR2_0",
                device="cuda" if torch.cuda.is_available() else "cpu",
            )
        except Exception as e:
            pytest.skip(f"无法加载GOT-OCR2_0模型: {str(e)}")

        # 创建图片信息列表
        images_info = [(1, sample_image), (2, sample_image)]

        # 处理图片
        results = processor.process_images(images_info)

        # 验证结果
        assert len(results) == 2
        assert all(text.strip() for _, text in results)

    def test_list_huggingface_models(self):
        """测试列出OCR模型"""
        models = OCRProcessor.list_huggingface_models()
        assert isinstance(models, list)
        assert len(models) > 0
        assert all(isinstance(model, str) for model in models)
        # 确保GOT-OCR2_0在列表中
        assert "stepfun-ai/GOT-OCR2_0" in models
