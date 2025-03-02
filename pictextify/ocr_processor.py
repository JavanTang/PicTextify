#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OCR处理模块 - 负责对图片进行文字识别，使用GOT-OCR2_0模型
"""

import os
import logging
from PIL import Image
import importlib.util
import torch

# 获取日志记录器
logger = logging.getLogger("pictextify.ocr_processor")


class OCRProcessor:
    """OCR处理类，负责对图片进行文字识别"""

    def __init__(self, lang=None, model_path=None, engine="got-ocr", device="cuda:0"):
        """
        初始化OCR处理器

        Args:
            lang (str, optional): OCR语言，对GOT-OCR2_0无效
            model_path (str, optional): GOT-OCR2_0模型路径
            engine (str): OCR引擎，默认为'got-ocr'
            device (str): 计算设备，强制使用'cpu'
        """
        self.model_path = model_path
        self.engine = engine
        self.device = "cuda:0"  # 强制使用CPU设备
        self.model = None
        self.tokenizer = None

        logger.info(f"初始化OCR处理器: engine={engine}, device=cpu")
        logger.debug(f"模型路径: {model_path}, 语言: {lang}")

        # 检查是否安装了transformers
        if not self._check_transformers():
            logger.error("未安装transformers库，无法使用GOT-OCR模型")
            raise ImportError(
                "使用GOT-OCR模型需要安装transformers库: pip install transformers"
            )

        # 加载GOT-OCR模型
        self._load_got_ocr_model()

    def _check_transformers(self):
        """检查是否安装了transformers库"""
        has_transformers = importlib.util.find_spec("transformers") is not None
        logger.debug(
            f"检查transformers库: {'已安装' if has_transformers else '未安装'}"
        )
        return has_transformers

    def _load_got_ocr_model(self, model_path=None, device="cuda:0"):
        """加载GOT-OCR2_0模型，强制使用CPU设备"""
        try:
            from transformers import AutoModel, AutoTokenizer

            logger.debug(f"PyTorch版本: {torch.__version__}")

            # 强制使用CPU设备
            self.device = "cuda:0"
            device = "cuda:0"

            # 如果没有指定模型，使用默认模型
            model_name = (
                model_path
                or self.model_path
                or "/home/tangzhifeng/MODELZOOS/GOT-OCR2_0"
            )
            logger.info(f"加载GOT-OCR2_0模型: {model_name}")

            # 加载tokenizer
            logger.debug("加载tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name, trust_remote_code=True
            )
            logger.debug("tokenizer加载完成")

            # 加载模型到CPU
            logger.debug(f"加载模型到CPU...")
            self.model = AutoModel.from_pretrained(
                model_name,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                device_map="cuda:0",  # 强制使用CPU
                use_safetensors=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
            self.model = self.model.eval()

            # 确认模型设备
            model_device = next(self.model.parameters()).device
            logger.info(f"模型已加载到设备: {model_device}")

            logger.info(f"已加载GOT-OCR2_0模型: {model_name}")
        except Exception as e:
            logger.error(f"加载GOT-OCR2_0模型时出错: {e}")
            raise ImportError(f"加载GOT-OCR2_0模型失败: {e}")

    def process_images(self, images_info):
        """
        处理图片列表，进行OCR识别

        Args:
            images_info (list): 图片信息列表，每个元素为(位置索引, 图片路径) 或 (位置索引, 图片路径, 位置信息)

        Returns:
            list: OCR结果列表，每个元素为(位置索引, OCR文本)
        """
        logger.info(f"开始处理 {len(images_info)} 张图片")
        ocr_results = []

        for image_info in images_info:
            position = image_info[0]
            image_path = image_info[1]
            logger.debug(f"处理图片: 索引={position}, 路径={image_path}")

            # 检查图片是否存在
            if not os.path.exists(image_path):
                logger.warning(f"图片不存在，跳过OCR处理: {image_path}")
                continue

            # 处理图片
            text = self.process_single_image(image_path)

            # 如果识别出文本，则添加到结果列表
            if text and text.strip():
                logger.debug(f"图片 {position} OCR成功，文本长度: {len(text)}")
                ocr_results.append((position, text))
            else:
                logger.warning(f"图片 {position} OCR结果为空")

        logger.info(f"图片处理完成，成功识别 {len(ocr_results)} 张图片")
        return ocr_results

    def process_single_image(self, image_path):
        """
        处理单张图片，进行OCR识别

        Args:
            image_path (str): 图片路径

        Returns:
            str: OCR识别结果
        """
        logger.debug(f"处理单张图片: {image_path}")
        try:
            # 检查图片是否存在
            if not os.path.exists(image_path):
                logger.warning(f"图片不存在: {image_path}")
                return ""

            # 检查图片是否可以打开
            try:
                img = Image.open(image_path)
                img_size = img.size
                logger.debug(f"图片尺寸: {img_size}")
                img.close()
            except Exception as e:
                logger.error(f"无法打开图片: {image_path}, 错误: {str(e)}")
                return ""

            # 使用GOT-OCR2_0进行OCR识别
            result = self._process_with_got_ocr(image_path)
            if result:
                logger.debug(f"OCR成功，结果长度: {len(result)}")
            else:
                logger.warning(f"OCR结果为空")
            return result
        except Exception as e:
            logger.exception(f"处理图片时出错: {str(e)}")
            return ""

    def _process_with_got_ocr(self, image_path):
        """使用GOT-OCR2_0模型处理图片"""
        try:
            logger.debug(f"处理单张图片: {image_path}")

            # 加载图片
            image = Image.open(image_path)
            logger.debug(f"图片尺寸: {image.size}")
            logger.debug(f"图像已加载: {image_path}")

            # 强制使用CPU设备
            self.device = "cuda:0"

            # 确保模型在CPU上
            model_device = next(self.model.parameters()).device
            logger.debug(f"当前模型设备: {model_device}")

            # 如果模型不在CPU上，移动到CPU
            if str(model_device) != "cuda:0":
                logger.info(f"将模型从 {model_device} 移动到 CPU")
                self.model.to("cuda:0")

            logger.debug("使用CPU设备进行OCR")

            import pdb

            # pdb.set_trace()

            # 使用模型进行OCR识别前，先打印详细信息
            logger.info(f"模型类型: {type(self.model)}")
            logger.info(f"模型设备: {next(self.model.parameters()).device}")

            # 尝试获取并打印input_ids的设备信息
            try:
                # 使用模型进行OCR识别
                result = self.model.chat(self.tokenizer, image_path, ocr_type="ocr")

                # 如果结果为空，返回默认文本
                if not result or result.strip() == "":
                    logger.warning(f"OCR结果为空: {image_path}")
                    result = "【图片文字无法识别】"

                logger.debug(f"OCR成功，结果长度: {len(result)}")
                return result
            except Exception as e:
                logger.error(f"OCR处理出错: {e}")
                # 尝试获取更多信息
                if hasattr(self.model, "device_map"):
                    logger.info(f"模型device_map: {self.model.device_map}")
                return "【图片文字无法识别】"

        except Exception as e:
            logger.error(f"OCR处理出错: {e}")
            return "【图片文字无法识别】"

    @staticmethod
    def list_huggingface_models():
        """
        列出推荐的OCR模型

        Returns:
            list: 推荐模型列表
        """
        models = ["stepfun-ai/GOT-OCR2_0"]
        logger.debug(f"推荐的OCR模型: {models}")
        return models
