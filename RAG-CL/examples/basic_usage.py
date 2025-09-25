#!/usr/bin/env python3
"""
RAG-CL基本使用示例

This example demonstrates basic usage of RAG-CL document parsing system.
"""

import logging
from pathlib import Path
from ragcl import RAGAnythingCL, RAGAnythingCLConfig

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """主函数演示RAG-CL基本用法"""
    
    # 1. 创建配置
    print("=== RAG-CL基本使用示例 ===\n")
    
    print("1. 创建配置...")
    config = RAGAnythingCLConfig(
        parser="mineru",  # 使用MinerU解析器
        working_dir="./output",
        parse_method="auto",
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
        batch_size=5,
        max_workers=2,
        output_format="json",
        save_intermediate=True
    )
    
    print(f"配置: 解析器={config.parser}, 工作目录={config.working_dir}")
    print(f"多模态处理: 图片={config.enable_image_processing}, 表格={config.enable_table_processing}")
    
    # 2. 初始化RAG-CL
    print("\n2. 初始化RAG-CL系统...")
    ragcl = RAGAnythingCL(config)
    
    # 检查安装状态
    if ragcl.check_installation():
        print("✅ 解析器安装检查通过")
    else:
        print("❌ 解析器安装检查失败，请确保MinerU已正确安装")
        return
    
    # 3. 获取系统信息
    print("\n3. 系统信息:")
    summary = ragcl.get_config_summary()
    print(f"支持的格式: {list(summary['supported_formats'].keys())}")
    
    # 4. 解析示例文档(这里使用假设的文件路径)
    print("\n4. 文档解析示例:")
    
    # 示例文件路径列表 - 实际使用时请替换为真实文件路径
    example_files = [
        "example.pdf",
        "document.docx", 
        "image.png",
        "table.xlsx"
    ]
    
    # 检查哪些文件实际存在
    existing_files = []
    for file_path in example_files:
        if Path(file_path).exists():
            existing_files.append(file_path)
    
    if existing_files:
        print(f"发现可解析文件: {existing_files}")
        
        # 解析单个文档
        try:
            print(f"\n解析单个文档: {existing_files[0]}")
            content_list = ragcl.parse_document(existing_files[0])
            
            print(f"✅ 成功解析，获得 {len(content_list)} 个内容块")
            
            # 显示内容块类型统计
            content_types = {}
            for item in content_list:
                if isinstance(item, dict):
                    content_type = item.get("type", "unknown")
                    content_types[content_type] = content_types.get(content_type, 0) + 1
            
            print("内容块类型分布:")
            for content_type, count in content_types.items():
                print(f"  - {content_type}: {count}")
            
        except Exception as e:
            print(f"❌ 解析失败: {str(e)}")
        
        # 批量解析(如果有多个文件)
        if len(existing_files) > 1:
            print(f"\n批量解析 {len(existing_files)} 个文档...")
            try:
                results = ragcl.parse_documents_batch(existing_files)
                
                total_blocks = sum(len(content) for content in results.values())
                print(f"✅ 批量解析完成，总共获得 {total_blocks} 个内容块")
                
                for file_path, content in results.items():
                    print(f"  {Path(file_path).name}: {len(content)} 个内容块")
                
            except Exception as e:
                print(f"❌ 批量解析失败: {str(e)}")
    
    else:
        print("⚠️  未找到示例文件，跳过实际解析步骤")
        print("请将文档文件放置在当前目录并修改文件路径以测试解析功能")
    
    # 5. 展示配置选项
    print("\n5. 配置示例:")
    print("支持的配置选项:")
    config_dict = config.to_dict()
    for key, value in config_dict.items():
        if key != "parser_kwargs":  # 跳过复杂字典
            print(f"  {key}: {value}")


def demonstrate_advanced_usage():
    """演示高级用法"""
    print("\n=== 高级用法示例 ===\n")
    
    # 1. 从环境文件加载配置
    print("1. 从环境文件加载配置...")
    # 创建示例环境文件
    env_content = """# RAG-CL配置文件
RAG_CL_WORKING_DIR=./advanced_output
RAG_CL_PARSER=mineru
RAG_CL_PARSE_METHOD=ocr
RAG_CL_ENABLE_IMAGE=true
RAG_CL_ENABLE_TABLE=true
RAG_CL_BATCH_SIZE=8
RAG_CL_MAX_WORKERS=4
RAG_CL_OUTPUT_FORMAT=markdown
"""
    
    env_file = Path(".env.example")
    env_file.write_text(env_content, encoding='utf-8')
    print(f"创建示例环境文件: {env_file}")
    
    try:
        config = RAGAnythingCLConfig.from_env_file(str(env_file))
        print(f"✅ 成功从环境文件加载配置")
        print(f"配置摘要: 解析器={config.parser}, 批处理大小={config.batch_size}")
    except Exception as e:
        print(f"❌ 环境文件加载失败: {str(e)}")
    
    # 2. 自定义解析参数
    print("\n2. 自定义解析参数示例...")
    config = RAGAnythingCLConfig(parser="mineru")
    ragcl = RAGAnythingCL(config)
    
    # 展示不同的解析参数
    print("MinerU支持的自定义参数:")
    print("  - backend: pipeline, vlm-transformers, vlm-sglang-engine")
    print("  - device: cpu, cuda, cuda:0, npu, mps")
    print("  - start_page/end_page: 指定页面范围")
    print("  - formula/table: 启用/禁用公式和表格识别")
    
    # 3. 不同输出格式
    print("\n3. 不同输出格式...")
    formats = ["json", "markdown"]
    for fmt in formats:
        config = RAGAnythingCLConfig(output_format=fmt, save_intermediate=True)
        print(f"  输出格式: {fmt}")


if __name__ == "__main__":
    # 运行基本示例
    main()
    
    # 运行高级示例
    demonstrate_advanced_usage()
    
    print("\n=== 示例结束 ===")
    print("更多信息请参考文档: README.md")