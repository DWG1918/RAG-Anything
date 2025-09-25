# RAG-CL: Document Parsing System

RAG-CL是基于RAG-Anything项目构建的文档解析系统，专门提取并适配了RAG-Anything中的文档解析功能。

## 项目简介

RAG-CL (RAG-Contrastive Learning) 是一个专门的文档解析系统，它直接采用RAG-Anything项目中成熟的文档解析方法，支持多种文档格式的解析和处理。

## 主要特性

- **多格式支持**: 支持PDF、图片、Office文档、HTML、文本等多种格式
- **双解析器**: 支持MinerU和Docling两种解析器
- **批处理**: 支持批量文档处理
- **多模态内容**: 处理文本、图片、表格、公式等多种内容类型
- **配置灵活**: 支持环境变量和配置文件
- **并发处理**: 支持多线程并发解析

## 安装

### 基本安装

```bash
pip install ragcl
```

### 安装可选依赖

```bash
# 安装所有功能
pip install 'ragcl[all]'

# 安装特定功能
pip install 'ragcl[image]'      # 图片处理
pip install 'ragcl[text]'       # 文本处理
pip install 'ragcl[docling]'    # Docling解析器
```

### 从源码安装

```bash
git clone https://github.com/HKUDS/RAG-Anything.git
cd RAG-Anything/RAG-CL
pip install -e .
```

## 外部依赖

### LibreOffice (Office文档处理)

Office文档 (.doc, .docx, .ppt, .pptx, .xls, .xlsx) 需要LibreOffice:

- **Windows**: 从 https://www.libreoffice.org/download/download/ 下载
- **macOS**: `brew install --cask libreoffice`
- **Ubuntu/Debian**: `sudo apt-get install libreoffice`

## 快速开始

### 基本使用

```python
from ragcl import RAGAnythingCL, RAGAnythingCLConfig

# 创建配置
config = RAGAnythingCLConfig(
    parser="mineru",  # 或 "docling"
    working_dir="./output",
    enable_image_processing=True,
    enable_table_processing=True
)

# 初始化RAG-CL
ragcl = RAGAnythingCL(config)

# 解析单个文档
content_list = ragcl.parse_document("document.pdf")
print(f"解析得到 {len(content_list)} 个内容块")

# 批量解析
file_paths = ["doc1.pdf", "doc2.docx", "image.png"]
results = ragcl.parse_documents_batch(file_paths)
```

### 命令行使用

```bash
# 解析单个文档
ragcl document.pdf --parser mineru --output ./output

# 查看支持的格式
ragcl --help

# 检查安装
ragcl --check --parser mineru
```

### 环境配置

创建 `.env` 文件:

```env
RAG_CL_WORKING_DIR=./ragcl_data
RAG_CL_PARSER=mineru
RAG_CL_PARSE_METHOD=auto
RAG_CL_ENABLE_IMAGE=true
RAG_CL_ENABLE_TABLE=true
RAG_CL_ENABLE_EQUATION=true
RAG_CL_MINERU_BACKEND=pipeline
RAG_CL_BATCH_SIZE=10
RAG_CL_MAX_WORKERS=4
```

然后使用:

```python
from ragcl import RAGAnythingCLConfig

# 从环境文件加载配置
config = RAGAnythingCLConfig.from_env_file(".env")
```

## 解析器对比

### MinerU解析器

- **优势**: 强大的PDF和图片OCR能力
- **支持格式**: PDF, 图片, Office文档(需LibreOffice转换)
- **特点**: 支持复杂布局、公式识别、表格提取

### Docling解析器

- **优势**: 直接处理Office文档和HTML
- **支持格式**: PDF, Office文档, HTML
- **特点**: 原生Office支持，结构化数据提取

## 支持的文档格式

| 格式类型 | 扩展名 | MinerU | Docling |
|---------|--------|--------|---------|
| PDF | .pdf | ✅ | ✅ |
| 图片 | .png, .jpg, .bmp, .tiff 等 | ✅ | ❌ |
| Office | .doc, .docx, .ppt, .pptx, .xls, .xlsx | ✅* | ✅ |
| HTML | .html, .htm, .xhtml | ❌ | ✅ |
| 文本 | .txt, .md | ✅* | ❌ |

*需要额外转换步骤

## 输出格式

解析后的内容以统一格式返回:

```python
[
    {
        "type": "text",
        "text": "文本内容",
        "page_idx": 0
    },
    {
        "type": "image", 
        "img_path": "/path/to/image.png",
        "image_caption": "图片说明",
        "page_idx": 0
    },
    {
        "type": "table",
        "table_body": [[...], [...]],
        "table_caption": "表格标题",
        "page_idx": 1
    },
    {
        "type": "equation",
        "text": "LaTeX公式",
        "page_idx": 1
    }
]
```

## 高级用法

### 自定义解析参数

```python
# MinerU特定参数
content_list = ragcl.parse_document(
    "document.pdf",
    backend="vlm-transformers",
    device="cuda:0",
    start_page=0,
    end_page=5
)

# 批处理配置
config = RAGAnythingCLConfig(
    batch_size=20,
    max_workers=8,
    save_intermediate=True,
    output_format="markdown"
)
```

### 检查系统状态

```python
# 检查解析器安装
if ragcl.check_installation():
    print("解析器安装正常")

# 获取支持的格式
formats = ragcl.get_supported_formats()
print(formats)

# 获取配置摘要
summary = ragcl.get_config_summary()
print(summary)
```

## 项目结构

```
RAG-CL/
├── ragcl/
│   ├── __init__.py
│   ├── ragcl.py          # 主类
│   ├── config.py         # 配置管理
│   └── parser.py         # 文档解析器(from RAG-Anything)
├── examples/             # 示例代码
├── tests/               # 测试用例
├── docs/                # 文档
├── pyproject.toml       # 项目配置
└── README.md           # 说明文档
```

## 开发指南

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/HKUDS/RAG-Anything.git
cd RAG-Anything/RAG-CL

# 安装开发依赖
pip install -e .[all]
pip install -e .[dev]

# 代码格式化
black .
isort .

# 类型检查
mypy .

# 运行测试
pytest
```

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

本项目基于 [RAG-Anything](https://github.com/HKUDS/RAG-Anything) 项目的文档解析功能构建，感谢原项目团队的优秀工作。

## 贡献

欢迎提交Issues和Pull Requests来改进项目。

## 联系方式

如有问题请提交Issue到: https://github.com/HKUDS/RAG-Anything/issues