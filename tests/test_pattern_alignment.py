#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模式对齐功能测试
"""

import os
import pytest
import tempfile
from pictextify import extract_and_align_pattern
from pictextify.text_merger import TextMerger


class TestPatternAlignment:
    """模式对齐功能测试类"""

    @pytest.fixture
    def sample_pdf(self):
        """获取样本PDF文件"""
        return os.path.join(os.path.dirname(__file__), "data", "example.pdf")

    @pytest.fixture
    def sample_docx(self):
        """获取样本Word文档"""
        return os.path.join(os.path.dirname(__file__), "data", "example.docx")

    def test_text_merger_align_pattern(self):
        """测试TextMerger的align_pattern方法"""
        # 创建测试数据
        text_content = [
            (1, "haha\n这是一段测试文本"),
            (3, "hhah\n另一段测试文本"),
            (5, "11hhh\n第三段测试文本"),
        ]

        ocr_results = [
            (2, "在中国作家协会的支持下"),
            (4, "在中国作家协会举办的活动中"),
            (6, "在中国作家协会成立100周年之际"),
        ]

        # 使用TextMerger的align_pattern方法
        merger = TextMerger()
        result = merger.align_pattern(text_content, ocr_results)

        # 打印结果
        print("\n模式对齐结果:")
        print(result)

        # 验证结果
        assert "<text>" in result
        assert "<image>" in result
        assert "haha" in result
        assert "在中国作家" in result
        assert "hhah" in result
        assert "11" in result

        # 验证顺序
        text_parts = result.split("<text>")
        image_parts = result.split("<image>")

        # 应该有3个文本部分和3个图片部分
        assert len(text_parts) == 4  # 包括开头的空字符串
        assert len(image_parts) == 4  # 包括开头的空字符串

    def test_extract_and_align_pattern_pdf(self, sample_pdf):
        """测试extract_and_align_pattern函数处理PDF"""
        # 跳过测试如果没有安装transformers
        try:
            import transformers
            import torch
        except ImportError:
            pytest.skip("Transformers库不可用")

        # 创建临时输出文件
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            output_file = temp_file.name

        try:
            # 使用extract_and_align_pattern函数
            result = extract_and_align_pattern(
                sample_pdf,
                output_file,
                device="cuda" if torch.cuda.is_available() else "cpu",
            )

            # 打印结果
            print("\nPDF模式对齐结果:")
            print(result)

            # 验证结果
            assert "<text>" in result
            assert "<image>" in result

            # 验证输出文件
            assert os.path.exists(output_file)
            with open(output_file, "r", encoding="utf-8") as f:
                file_content = f.read()
                assert file_content == result

        finally:
            # 清理临时文件
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_extract_and_align_pattern_docx(self, sample_docx):
        """测试extract_and_align_pattern函数处理Word文档"""
        # 跳过测试如果没有安装transformers
        try:
            import transformers
            import torch
        except ImportError:
            pytest.skip("Transformers库不可用")

        # 创建临时输出文件
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            output_file = temp_file.name

        try:
            # 使用extract_and_align_pattern函数
            result = extract_and_align_pattern(
                sample_docx,
                output_file,
                device="cuda" if torch.cuda.is_available() else "cpu",
            )

            # 打印结果
            print("\nWord文档模式对齐结果:")
            print(result)

            # 验证结果
            assert "<text>" in result or "<image>" in result

            # 验证输出文件
            assert os.path.exists(output_file)
            with open(output_file, "r", encoding="utf-8") as f:
                file_content = f.read()
                assert file_content == result

        finally:
            # 清理临时文件
            if os.path.exists(output_file):
                os.unlink(output_file)
