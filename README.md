# PicTextify

[English](#english) | [中文](#chinese)

<a name="english"></a>

## English

PicTextify is a document processing tool that extracts text and images from PDF and Word documents, performs OCR on the images, and outputs complete plain text content.

### Features

1. **File Input and Type Detection**
   - Support for importing PDF and Word files via command line, file drag-and-drop
   - Automatic file type detection with error messages for unsupported file types

2. **File Parsing and Content Extraction**
   - PDF file parsing: Extract text content and images page by page, preserving position information
   - Word file parsing: Extract headings, table of contents, body text, and images
   - Save images to a temporary folder and record position information

3. **OCR Image Text Recognition**
   - Process extracted images with OCR
   - Support for multiple OCR engines: Tesseract and GOT-OCR
   - Support for custom OCR models and languages
   - CPU-based processing for maximum compatibility
   - Convert recognized text into editable text format

4. **Text Merging and Output**
   - Merge directly extracted text with OCR-recognized text in the original file's logical order
   - Output as plain text file (TXT format)

### Installation

#### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/PicTextify.git
cd PicTextify

# Install
pip install -e .
```

### Usage

#### As a Command Line Tool

```bash
# Basic usage
pictextify --input your_document.pdf --output result.txt

# Using Tesseract OCR engine (default)
pictextify --input your_document.pdf --ocr-engine tesseract --ocr-lang eng

# Using GOT-OCR engine
pictextify --input your_document.pdf --ocr-engine got-ocr

# Debug mode
pictextify --input your_document.pdf --output result.txt --debug
```

#### As a Python Library

```python
import pictextify

# Extract text and save to file
pictextify.extract_from_file('your_document.pdf', 'result.txt')

# Extract text without saving to file
text = pictextify.extract_from_file('your_document.pdf')
print(text)

# Using Tesseract OCR engine
text = pictextify.extract_from_file(
    'your_document.pdf',
    ocr_model='/path/to/tessdata',
    ocr_lang='eng',
    ocr_engine='tesseract'
)

# Using GOT-OCR engine
text = pictextify.extract_from_file(
    'your_document.pdf',
    ocr_engine='got-ocr'
)
```

### Parameters

- `--input`, `-i`: Input file path (PDF or DOCX format)
- `--output`, `-o`: Output text file path (defaults to input filename.txt)
- `--ocr-engine`: OCR engine, options: 'tesseract' or 'got-ocr'
- `--ocr-model`: OCR model path or name
- `--ocr-lang`: OCR language (default is chi_sim+eng)
- `--debug`: Enable debug mode for detailed logging
- `--version`, `-v`: Show version information

### Dependencies

- `PyMuPDF`: PDF file parsing
- `python-docx`: Word document parsing
- `pytesseract`: Tesseract OCR engine interface
- `torch`: PyTorch deep learning framework
- `Pillow`: Image processing

### Project Structure

```
PicTextify/
├── pictextify/                # Main package
│   ├── __init__.py            # Package initialization file
│   ├── cli.py                 # Command line interface
│   ├── file_handler.py        # File handling module
│   ├── pdf_processor.py       # PDF processing module
│   ├── docx_processor.py      # Word processing module
│   ├── ocr_processor.py       # OCR processing module
│   └── text_merger.py         # Text merging module
├── tests/                     # Test directory
│   ├── data/                  # Test data
│   ├── test_file_handler.py   # File handling module tests
│   ├── test_pdf_processor.py  # PDF processing module tests
│   └── test_ocr_processor.py  # OCR processing module tests
├── setup.py                   # Installation script
├── requirements.txt           # Dependency list
└── README.md                  # Project documentation
```

### OCR Engines

#### Tesseract OCR

PicTextify uses Tesseract OCR engine by default for image text recognition. You can download and use custom Tesseract language models:

1. Download language models from [Tesseract GitHub](https://github.com/tesseract-ocr/tessdata)
2. Place the downloaded model files (.traineddata) in the specified directory
3. Use the `--ocr-model` parameter to specify the model directory

#### GOT-OCR

PicTextify also supports using the GOT-OCR engine, which is optimized for Chinese and English text recognition:

1. Use the `--ocr-engine got-ocr` parameter to select the GOT-OCR engine
2. The model will be automatically downloaded and used

### Testing

Run tests:

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_file_handler.py

# Generate test coverage report
pytest --cov=pictextify
```

### License

MIT

---

<a name="chinese"></a>

## 中文

PicTextify是一个文档处理工具，能够从PDF和Word文档中提取文本和图片，并对图片进行OCR处理，最终输出完整的纯文本内容。

### 功能特点

1. **文件接收与类型判断**
   - 支持通过命令行、文件拖拽等方式导入PDF和Word文件
   - 自动判断文件类型，对不支持的文件类型给出错误提示

2. **文件解析与内容提取**
   - PDF文件解析：逐页提取文本内容和图片，保留位置信息
   - Word文件解析：提取标题、目录、正文和图片
   - 保存图片到临时文件夹，并记录位置信息

3. **OCR图片文字识别**
   - 对提取的图片进行OCR处理
   - 支持多种OCR引擎：Tesseract和GOT-OCR
   - 支持自定义OCR模型和语言
   - 基于CPU处理以获得最大兼容性
   - 将识别出的文字转换为可编辑的文本格式

4. **文本合并与输出**
   - 将直接提取的文本与OCR识别的文本按原文件逻辑顺序合并
   - 输出为纯文本文件(TXT格式)

### 安装

#### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/PicTextify.git
cd PicTextify

# 安装
pip install -e .
```

### 使用方法

#### 作为命令行工具使用

```bash
# 基本用法
pictextify --input your_document.pdf --output result.txt

# 使用Tesseract OCR引擎（默认）
pictextify --input your_document.pdf --ocr-engine tesseract --ocr-lang eng

# 使用GOT-OCR引擎
pictextify --input your_document.pdf --ocr-engine got-ocr

# 调试模式
pictextify --input your_document.pdf --output result.txt --debug
```

#### 作为Python库使用

```python
import pictextify

# 提取文本并保存到文件
pictextify.extract_from_file('your_document.pdf', 'result.txt')

# 提取文本但不保存到文件
text = pictextify.extract_from_file('your_document.pdf')
print(text)

# 使用Tesseract OCR引擎
text = pictextify.extract_from_file(
    'your_document.pdf',
    ocr_model='/path/to/tessdata',
    ocr_lang='eng',
    ocr_engine='tesseract'
)

# 使用GOT-OCR引擎
text = pictextify.extract_from_file(
    'your_document.pdf',
    ocr_engine='got-ocr'
)
```

### 参数说明

- `--input`, `-i`: 输入文件路径(PDF或DOCX格式)
- `--output`, `-o`: 输出文本文件路径(默认为input文件名.txt)
- `--ocr-engine`: OCR引擎，可选 'tesseract' 或 'got-ocr'
- `--ocr-model`: OCR模型路径或名称
- `--ocr-lang`: OCR语言(默认为chi_sim+eng)
- `--debug`: 启用调试模式以获取详细日志
- `--version`, `-v`: 显示版本信息

### 依赖库

- `PyMuPDF`: PDF文件解析
- `python-docx`: Word文档解析
- `pytesseract`: Tesseract OCR引擎接口
- `torch`: PyTorch深度学习框架
- `Pillow`: 图像处理

### 项目结构

```
PicTextify/
├── pictextify/                # 主包
│   ├── __init__.py            # 包初始化文件
│   ├── cli.py                 # 命令行接口
│   ├── file_handler.py        # 文件处理模块
│   ├── pdf_processor.py       # PDF处理模块
│   ├── docx_processor.py      # Word处理模块
│   ├── ocr_processor.py       # OCR处理模块
│   └── text_merger.py         # 文本合并模块
├── tests/                     # 测试目录
│   ├── data/                  # 测试数据
│   ├── test_file_handler.py   # 文件处理模块测试
│   ├── test_pdf_processor.py  # PDF处理模块测试
│   └── test_ocr_processor.py  # OCR处理模块测试
├── setup.py                   # 安装脚本
├── requirements.txt           # 依赖库列表
└── README.md                  # 项目说明
```

### OCR引擎

#### Tesseract OCR

PicTextify默认使用Tesseract OCR引擎进行图片文字识别。您可以下载并使用自定义的Tesseract语言模型：

1. 从[Tesseract GitHub](https://github.com/tesseract-ocr/tessdata)下载语言模型
2. 将下载的模型文件(.traineddata)放置到指定目录
3. 使用`--ocr-model`参数指定模型目录

#### GOT-OCR

PicTextify还支持使用GOT-OCR引擎，该引擎针对中英文文本识别进行了优化：

1. 使用`--ocr-engine got-ocr`参数选择GOT-OCR引擎
2. 模型将自动下载并使用

### 测试

运行测试：

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_file_handler.py

# 生成测试覆盖率报告
pytest --cov=pictextify
```

### 许可证

MIT 