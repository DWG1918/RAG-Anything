# RAG-CL 实体提取功能

RAG-CL项目已成功集成了基于RAG-Anything的实体提取功能，支持从解析后的文档中提取结构化实体和关系信息。

## 功能特性

### 🎯 核心功能
- **多模态实体提取**: 支持从文本、表格等不同类型的内容块中提取实体
- **关系识别**: 自动识别实体间的语义关系
- **文档结构分析**: 提供文档级别的元信息分析
- **LLM驱动**: 基于GPT等大语言模型进行智能分析

### 📊 支持的内容类型
- **文本块**: 提取概念、术语、人名、地名等实体
- **表格数据**: 从结构化数据中提取关键参数和数值
- **文档结构**: 分析整体文档特征和组织结构

### 🔗 实体关系类型
- `part_of`: 部分关系
- `related_to`: 相关关系  
- `depends_on`: 依赖关系
- `defines`: 定义关系
- `measures`: 度量关系

## 快速开始

### 基本用法

```python
from ragcl import RAGAnythingCL, RAGAnythingCLConfig

# 创建配置
config = RAGAnythingCLConfig(
    working_dir="./output",
    save_intermediate=True
)

# 初始化系统
ragcl = RAGAnythingCL(config)

# 方式1: 对已解析内容进行实体提取
content_list = ragcl.parse_document("document.pdf")
entities_result = ragcl.extract_entities(content_list)

# 方式2: 一体化处理（解析+实体提取）
complete_result = ragcl.parse_and_extract_entities("document.pdf")
```

### 结果结构

实体提取返回以下结构化数据：

```python
{
    "entities": [
        {
            "name": "实体名称",
            "type": "实体类型",
            "description": "实体描述", 
            "relevance_score": 0.95,
            "source_page": 1,
            "source_type": "text"
        }
    ],
    "relationships": [
        {
            "from": "实体1",
            "to": "实体2",
            "relation": "related_to",
            "description": "关系描述",
            "confidence": 0.8
        }
    ],
    "document_analysis": {
        "document_info": {
            "title": "文档标题",
            "type": "文档类型",
            "domain": "领域",
            "language": "语言"
        }
    },
    "statistics": {
        "total_entities": 15,
        "total_relationships": 8,
        "text_blocks_processed": 10,
        "table_blocks_processed": 3
    }
}
```

## API配置

### LLM设置

系统默认使用以下API配置：
- **API Base**: `https://api.chatanywhere.tech/v1`
- **Model**: `gpt-3.5-turbo`
- **API Key**: 已配置默认密钥

### 自定义配置

```python
from ragcl import EntityExtractor

# 自定义LLM配置
extractor = EntityExtractor(
    api_base="https://your-api-url.com/v1",
    api_key="your-api-key", 
    model="gpt-4"
)
```

## 示例脚本

### 1. 基本演示
```bash
python examples/simple_entity_demo.py
```

### 2. 完整测试
```bash
python examples/entity_extraction_test.py
```

### 3. 集成到基本用法
```bash
python examples/basic_usage.py
```

## 输出文件

当启用`save_intermediate=True`时，系统会保存：

- `{filename}_complete_results.json`: 完整处理结果
- `{filename}_entities.json`: 实体提取结果
- `{filename}_parsed.json`: 文档解析结果

## 性能说明

- **实体提取速度**: 取决于文档大小和LLM响应时间
- **支持批处理**: 可并行处理多个文档
- **内存优化**: 自动合并短文本块以提高效率
- **错误处理**: 具备完善的异常处理机制

## 技术架构

### 核心组件

1. **EntityExtractor**: 实体提取核心引擎
2. **RAGAnythingCL**: 主接口类，集成解析和提取功能
3. **Prompt Templates**: 优化的中文提示模板
4. **Response Parser**: JSON响应解析和验证

### 处理流程

```
文档输入 → 文档解析 → 内容分类 → 实体提取 → 关系分析 → 结果输出
    ↓         ↓         ↓         ↓         ↓         ↓
   PDF      内容块    文本/表格   实体列表   关系列表   结构化输出
```

## 注意事项

1. **API依赖**: 需要有效的OpenAI兼容API配置
2. **网络连接**: 实体提取需要稳定的网络连接
3. **处理时间**: 大文档的实体提取可能需要较长时间
4. **语言支持**: 当前主要优化为中文内容

## 版本信息

- **RAG-CL版本**: 0.1.0
- **OpenAI库版本**: >=1.0.0 (新版API格式)
- **支持的文档格式**: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, 图片格式等

## 更新日志

### v0.1.0 (2025-09-25)
- ✅ 首次发布实体提取功能
- ✅ 集成RAG-Anything的实体提取算法
- ✅ 支持多模态内容处理
- ✅ 更新OpenAI API到v1.0+格式
- ✅ 添加完整的测试脚本和演示
- ✅ 实现中文优化的提示模板