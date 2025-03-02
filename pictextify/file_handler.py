#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件处理模块 - 负责文件类型判断和基本文件操作
"""

import os
import mimetypes

class FileHandler:
    """文件处理类，负责文件类型判断和基本文件操作"""
    
    def __init__(self):
        """初始化，确保mimetypes已初始化"""
        mimetypes.init()
    
    def get_file_type(self, file_path):
        """
        根据文件扩展名判断文件类型
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            str: 文件类型 ('pdf', 'docx' 或 None)
        """
        # 获取文件扩展名并转为小写
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.pdf':
            return 'pdf'
        elif ext == '.docx':
            return 'docx'
        else:
            return None
    
    def validate_file(self, file_path):
        """
        验证文件是否存在且是否为支持的类型
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False, f"文件 '{file_path}' 不存在"
        
        # 检查文件是否为常规文件
        if not os.path.isfile(file_path):
            return False, f"'{file_path}' 不是一个文件"
        
        # 检查文件类型
        file_type = self.get_file_type(file_path)
        if file_type not in ['pdf', 'docx']:
            return False, f"不支持的文件类型，仅支持PDF和DOCX格式"
        
        return True, None 