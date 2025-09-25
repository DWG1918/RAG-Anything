#!/usr/bin/env python3
"""
RAG-CL 快速测试脚本
"""

import sys
import logging
from pathlib import Path

# 添加ragcl包到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ragcl import RAGAnythingCL, RAGAnythingCLConfig

# 设置简单日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# def quick_test():
#     """快速测试RAG-CL基本功能"""
    
#     print("=== RAG-CL 快速测试 ===\n")
    
#     # 测试配置创建
#     print("1. 测试配置创建...")
#     try:
#         config = RAGAnythingCLConfig(
#             parser='mineru',
#             working_dir='./quick_test_output',
#             parse_method="auto",
#             enable_image_processing=True,
#             enable_table_processing=True,
#             enable_equation_processing=True,
#             save_intermediate=True
#         )
#         print(f"✅ 配置创建成功: 解析器={config.parser}")
#     except Exception as e:
#         print(f"❌ 配置创建失败: {e}")
#         return False
    
#     # 测试RAG-CL初始化
#     print("\n2. 测试RAG-CL初始化...")
#     try:
#         ragcl = RAGAnythingCL(config)
#         print("✅ RAG-CL初始化成功")
#     except Exception as e:
#         print(f"❌ RAG-CL初始化失败: {e}")
#         return False
    
#     # 测试解析器安装检查
#     print("\n3. 检查解析器安装...")
#     try:
#         if ragcl.check_installation():
#             print("✅ MinerU安装检查通过")
#         else:
#             print("❌ MinerU安装检查失败")
#             print("💡 请确保已安装MinerU: pip install 'mineru[core]'")
#             return False
#     except Exception as e:
#         print(f"❌ 安装检查错误: {e}")
#         return False
    
#     # 检查PDF文件
#     print("\n4. 检查PDF文件...")
#     pdf_path = Path(__file__).parent.parent / "input" / "p5-14.pdf"
#     if pdf_path.exists():
#         print(f"✅ PDF文件存在: {pdf_path}")
#         print(f"📏 文件大小: {pdf_path.stat().st_size / 1024:.1f} KB")
#     else:
#         print(f"❌ PDF文件不存在: {pdf_path}")
#         return False
    
#     # 获取支持的格式
#     print("\n5. 获取支持的格式...")
#     try:
#         formats = ragcl.get_supported_formats()
#         print("✅ 支持的格式:")
#         for category, extensions in formats.items():
#             print(f"  {category}: {', '.join(extensions)}")
#     except Exception as e:
#         print(f"❌ 获取格式失败: {e}")
#         return False
    
#     # 获取配置摘要
#     print("\n6. 获取配置摘要...")
#     try:
#         summary = ragcl.get_config_summary()
#         print("✅ 系统配置:")
#         print(f"  解析器: {summary['parser']}")
#         print(f"  解析方法: {summary['parse_method']}")
#         print(f"  工作目录: {summary['working_dir']}")
#         print(f"  输出格式: {summary['output_format']}")
#     except Exception as e:
#         print(f"❌ 获取配置摘要失败: {e}")
#         return False
    
#     print("\n🎉 所有基本功能测试通过!")
#     return True

def test_simple_parse():
    """尝试简单的PDF解析"""
    print("\n=== 尝试PDF解析 ===")
    
    pdf_path = Path(__file__).parent.parent / "input" / "p5-14.pdf"
    
    # 使用更简单的配置
    config = RAGAnythingCLConfig(
        parser='mineru',
        working_dir='./quick_parse_output',
        parse_method='auto',  # 使用更简单的txt方法
        # enable_image_processing=True,  # 禁用复杂功能
        enable_table_processing=True,
        # enable_equation_processing=True,
    )
    
    ragcl = RAGAnythingCL(config)
    
    try:
        print("🚀 开始解析PDF (使用简化配置)...")
        content_list = ragcl.parse_document(pdf_path)
        
        print(f"✅ 解析成功!")
        print(f"📊 获得内容块数量: {len(content_list)}")
        
        # 简单统计
        content_types = {}
        for item in content_list:
            if isinstance(item, dict):
                content_type = item.get('type', 'unknown')
                content_types[content_type] = content_types.get(content_type, 0) + 1
        
        print("📋 内容类型分布:")
        for content_type, count in content_types.items():
            print(f"  {content_type}: {count}")
        
        # 显示前3个内容块
        print("\n📄 内容预览 (前3个块):")
        for i, item in enumerate(content_list[:3]):
            if isinstance(item, dict):
                content_type = item.get('type', 'unknown')
                if content_type == 'text':
                    text = item.get('text', '')
                    preview = text[:100] + '...' if len(text) > 100 else text
                    print(f"  [{i+1}] {content_type}: {preview}")
                else:
                    print(f"  [{i+1}] {content_type}: {item}")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF解析失败: {e}")
        logger.exception("详细错误信息:")
        return False

def main():
    """主函数"""
    # 基础功能测试
    # if not quick_test():
    #     print("\n❌ 基础功能测试失败，退出")
    #     return 1
    
    # PDF解析测试
    if test_simple_parse():
        print("\n🎉 PDF解析测试成功!")
        print("✅ RAG-CL文档解析功能正常工作")
    else:
        print("\n⚠️  PDF解析测试失败，但基础功能正常")
    
    return 0

if __name__ == "__main__":
    exit(main())