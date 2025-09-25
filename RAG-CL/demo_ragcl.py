#!/usr/bin/env python3
"""
RAG-CL 功能演示脚本

演示RAG-CL系统的核心功能和特性
"""

import sys
import json
from pathlib import Path

# 添加ragcl包到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from ragcl import RAGAnythingCL, RAGAnythingCLConfig

def demo_configuration():
    """演示配置功能"""
    print("=== 1. 配置系统演示 ===\n")
    
    # 默认配置
    print("📋 默认配置:")
    config_default = RAGAnythingCLConfig()
    print(f"  解析器: {config_default.parser}")
    print(f"  工作目录: {config_default.working_dir}")
    print(f"  解析方法: {config_default.parse_method}")
    
    # 自定义配置
    print(f"\n📋 自定义配置:")
    config_custom = RAGAnythingCLConfig(
        parser='mineru',
        working_dir='./custom_output',
        parse_method='auto',
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
        batch_size=5,
        max_workers=2,
        output_format='json'
    )
    
    print(f"  解析器: {config_custom.parser}")
    print(f"  多模态处理: 图片={config_custom.enable_image_processing}, 表格={config_custom.enable_table_processing}")
    print(f"  批处理配置: 批量大小={config_custom.batch_size}, 最大工作线程={config_custom.max_workers}")
    
    # 配置转换为字典
    print(f"\n📋 配置字典形式:")
    config_dict = config_custom.to_dict()
    key_configs = ['parser', 'parse_method', 'enable_image_processing', 'batch_size']
    for key in key_configs:
        print(f"  {key}: {config_dict[key]}")
    
    return config_custom

def demo_ragcl_init(config):
    """演示RAG-CL初始化"""
    print(f"\n=== 2. RAG-CL系统初始化 ===\n")
    
    # 初始化RAG-CL
    print("🚀 初始化RAG-CL系统...")
    ragcl = RAGAnythingCL(config)
    print("✅ RAG-CL初始化成功")
    
    # 检查安装状态
    print(f"\n🔍 检查解析器安装状态...")
    installation_ok = ragcl.check_installation()
    if installation_ok:
        print(f"✅ {config.parser} 解析器安装正常")
    else:
        print(f"⚠️  {config.parser} 解析器可能未正确安装")
    
    return ragcl, installation_ok

def demo_formats_and_capabilities(ragcl):
    """演示支持的格式和能力"""
    print(f"\n=== 3. 支持格式和能力演示 ===\n")
    
    # 获取支持的格式
    print("📁 支持的文档格式:")
    formats = ragcl.get_supported_formats()
    for category, extensions in formats.items():
        print(f"  {category}: {', '.join(extensions)}")
    
    # 获取系统配置摘要
    print(f"\n⚙️ 系统配置摘要:")
    summary = ragcl.get_config_summary()
    
    print(f"  当前解析器: {summary['parser']}")
    print(f"  解析方法: {summary['parse_method']}")
    print(f"  工作目录: {summary['working_dir']}")
    print(f"  输出格式: {summary['output_format']}")
    
    print(f"\n🔧 多模态处理能力:")
    multimodal = summary['multimodal_processing']
    print(f"  图片处理: {'✅' if multimodal['images'] else '❌'}")
    print(f"  表格处理: {'✅' if multimodal['tables'] else '❌'}")
    print(f"  公式处理: {'✅' if multimodal['equations'] else '❌'}")
    
    print(f"\n📊 批处理配置:")
    batch_settings = summary['batch_settings']
    print(f"  批处理大小: {batch_settings['batch_size']}")
    print(f"  最大工作线程: {batch_settings['max_workers']}")

def demo_mock_parsing_results():
    """演示模拟的解析结果结构"""
    print(f"\n=== 4. 解析结果结构演示 ===\n")
    
    # 模拟解析结果
    mock_results = [
        {
            "type": "text",
            "text": "Standard SGT-100-2S Driver Package Acoustic Equipment Technical Requirement Specification",
            "page_idx": 0
        },
        {
            "type": "text", 
            "text": "Siemens product development has developed a standardised package solution. The aims of this project are to: Create a product that is structured to fit varied markets through the use of pre engineered options",
            "page_idx": 0
        },
        {
            "type": "table",
            "table_caption": "Environmental design limits",
            "table_body": [
                ["Parameter", "Onshore", "Coastal", "Offshore"],
                ["Standard temperature range(°C)", "-20 +43", "-20 +43", "-20 +43"],
                ["High temperature option(°C)", "-15 +55", "-15 +55", "-15 +55"]
            ],
            "page_idx": 1
        },
        {
            "type": "image",
            "img_path": "/path/to/extracted/image.png",
            "image_caption": "Siemens logo and header",
            "page_idx": 0
        }
    ]
    
    print("📄 解析结果示例结构:")
    print(f"总内容块数: {len(mock_results)}")
    
    # 统计内容类型
    content_types = {}
    for item in mock_results:
        content_type = item['type']
        content_types[content_type] = content_types.get(content_type, 0) + 1
    
    print(f"\n📊 内容类型分布:")
    for content_type, count in content_types.items():
        print(f"  {content_type}: {count}")
    
    print(f"\n📋 详细内容示例:")
    for i, item in enumerate(mock_results):
        print(f"  [{i+1}] 类型: {item['type']}, 页面: {item['page_idx']}")
        if item['type'] == 'text':
            preview = item['text'][:80] + '...' if len(item['text']) > 80 else item['text']
            print(f"      内容: {preview}")
        elif item['type'] == 'table':
            print(f"      表格: {item['table_caption']}")
            print(f"      行数: {len(item['table_body'])}")
        elif item['type'] == 'image':
            print(f"      图片: {item['image_caption']}")
    
    return mock_results

def demo_output_formats(mock_results):
    """演示输出格式"""
    print(f"\n=== 5. 输出格式演示 ===\n")
    
    # JSON格式
    print("📝 JSON格式输出示例:")
    json_sample = json.dumps(mock_results[0], ensure_ascii=False, indent=2)
    print(json_sample)
    
    # Markdown格式转换示例
    print(f"\n📝 Markdown格式输出示例:")
    print("```markdown")
    for item in mock_results[:2]:  # 只显示前两个
        if item['type'] == 'text':
            print(item['text'])
            print()
        elif item['type'] == 'table':
            print(f"**{item['table_caption']}**")
            print()
            # 简化的表格格式
            for row in item['table_body'][:2]:  # 只显示前两行
                print(f"| {' | '.join(row)} |")
            print()
    print("```")

def demo_practical_usage():
    """演示实际使用场景"""
    print(f"\n=== 6. 实际使用场景演示 ===\n")
    
    print("🔧 典型使用流程:")
    print("1. 创建配置对象")
    print("   config = RAGAnythingCLConfig(parser='mineru', ...)")
    
    print("2. 初始化RAG-CL系统")
    print("   ragcl = RAGAnythingCL(config)")
    
    print("3. 解析单个文档")
    print("   content_list = ragcl.parse_document('document.pdf')")
    
    print("4. 批量解析文档")  
    print("   results = ragcl.parse_documents_batch(['doc1.pdf', 'doc2.docx'])")
    
    print(f"\n📋 解析器选择建议:")
    print("• MinerU适用于:")
    print("  - PDF文档的高精度解析")
    print("  - 图片和扫描文档的OCR")
    print("  - 复杂版式的科技文档")
    print("  - 需要公式和表格识别")
    
    print("• Docling适用于:")
    print("  - Office文档的原生解析")
    print("  - HTML网页内容提取")
    print("  - 结构化文档处理")
    print("  - 快速批量处理")

def main():
    """主演示函数"""
    print("🎯 RAG-CL 文档解析系统功能演示\n")
    print("基于RAG-Anything项目的文档解析功能构建")
    print("=" * 50)
    
    # 1. 配置演示
    config = demo_configuration()
    
    # 2. 系统初始化演示
    ragcl, installation_ok = demo_ragcl_init(config)
    
    # 3. 格式和能力演示
    demo_formats_and_capabilities(ragcl)
    
    # 4. 解析结果演示
    mock_results = demo_mock_parsing_results()
    
    # 5. 输出格式演示
    demo_output_formats(mock_results)
    
    # 6. 实际使用场景
    demo_practical_usage()
    
    # 总结
    print(f"\n" + "=" * 50)
    print("📋 功能总结:")
    print("✅ 配置系统 - 灵活的参数配置")
    print("✅ 解析器支持 - MinerU和Docling双引擎")
    print("✅ 多格式支持 - PDF、Office、图片、HTML等")
    print("✅ 多模态处理 - 文本、图片、表格、公式")
    print("✅ 批量处理 - 并发处理多个文档")
    print("✅ 统一接口 - 简洁易用的API")
    
    if installation_ok:
        print(f"\n🎉 系统就绪，可以进行实际的文档解析!")
        print(f"💡 使用 python quick_test.py 进行实际PDF解析测试")
    else:
        print(f"\n⚠️  解析器可能需要安装，请参考README.md")
    
    # 检查PDF文件
    pdf_path = Path(__file__).parent / "input" / "p5-14.pdf" 
    if pdf_path.exists():
        print(f"📄 测试PDF已就绪: {pdf_path.name} ({pdf_path.stat().st_size/1024:.1f} KB)")
    
    return 0

if __name__ == "__main__":
    exit(main())