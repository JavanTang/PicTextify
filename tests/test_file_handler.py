#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件处理模块测试
"""

import os
import pytest
from pictextify.file_handler import FileHandler

class TestFileHandler:
    """文件处理类测试"""
    
    def test_get_file_type(self):
        """测试文件类型判断"""
        handler = FileHandler()
        
        # 测试PDF文件
        assert handler.get_file_type('test.pdf') == 'pdf'
        assert handler.get_file_type('test.PDF') == 'pdf'
        
        # 测试Word文件
        assert handler.get_file_type('test.docx') == 'docx'
        assert handler.get_file_type('test.DOCX') == 'docx'
        
        # 测试不支持的文件类型
        assert handler.get_file_type('test.txt') is None
        assert handler.get_file_type('test.jpg') is None
    
    def test_validate_file(self, tmp_path):
        """测试文件验证"""
        handler = FileHandler()
        
        # 创建测试文件
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("PDF test content")
        
        docx_file = tmp_path / "test.docx"
        docx_file.write_text("DOCX test content")
        
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("TXT test content")
        
        # 测试有效文件
        is_valid, _ = handler.validate_file(str(pdf_file))
        assert is_valid is True
        
        is_valid, _ = handler.validate_file(str(docx_file))
        assert is_valid is True
        
        # 测试不支持的文件类型
        is_valid, error = handler.validate_file(str(txt_file))
        assert is_valid is False
        assert "不支持的文件类型" in error
        
        # 测试不存在的文件
        is_valid, error = handler.validate_file(str(tmp_path / "nonexistent.pdf"))
        assert is_valid is False
        assert "不存在" in error 