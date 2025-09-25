#!/usr/bin/env python3
"""
Entity Extraction Test Script

This script tests the entity extraction functionality of RAG-CL.
It can test entity extraction on previously parsed content or parse and extract in one step.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import json
from ragcl import RAGAnythingCL, RAGAnythingCLConfig

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_entity_extraction_with_parsed_content():
    """测试使用已解析内容进行实体提取"""
    print("=== 测试实体提取功能（使用已解析内容）===\n")
    
    # 创建模拟的已解析内容
    sample_content = [
        {
            "type": "text",
            "text": "本文档介绍了深度学习中的卷积神经网络(CNN)架构。CNN在图像识别任务中表现优异，特别是在ImageNet数据集上取得了显著的成果。",
            "page_idx": 0,
            "block_index": 0
        },
        {
            "type": "text", 
            "text": "ResNet-50是一种经典的深度残差网络，由微软研究院于2015年提出。该网络通过引入残差连接解决了深层网络的梯度消失问题。",
            "page_idx": 0,
            "block_index": 1
        },
        {
            "type": "table",
            "table_caption": "深度学习模型性能对比",
            "table_body": [
                ["模型名称", "参数量", "Top-1准确率", "Top-5准确率"],
                ["ResNet-50", "25.6M", "76.15%", "92.87%"],
                ["VGG-16", "138M", "71.59%", "90.38%"],
                ["AlexNet", "60M", "57.10%", "80.30%"]
            ],
            "page_idx": 1,
            "block_index": 2
        },
        {
            "type": "text",
            "text": "Transformer架构自2017年被提出以来，在自然语言处理领域取得了革命性的进展。BERT、GPT等模型都基于Transformer架构。",
            "page_idx": 1,
            "block_index": 3
        }
    ]
    
    print(f"模拟内容块数量: {len(sample_content)}")
    
    # 初始化RAG-CL系统
    config = RAGAnythingCLConfig(
        working_dir="./output",
        save_intermediate=True
    )
    ragcl = RAGAnythingCL(config)
    
    try:
        # 测试实体提取
        print("\n开始实体提取...")
        entities_result = ragcl.extract_entities(sample_content, extract_relations=True)
        
        # 显示结果
        print(f"\n✅ 实体提取完成!")
        print(f"提取到的实体数量: {entities_result['statistics']['total_entities']}")
        print(f"提取到的关系数量: {entities_result['statistics']['total_relationships']}")
        
        # 显示前几个实体
        entities = entities_result.get('entities', [])
        if entities:
            print(f"\n前5个实体示例:")
            for i, entity in enumerate(entities[:5]):
                print(f"  {i+1}. {entity.get('name', 'N/A')} ({entity.get('type', 'N/A')})")
                if entity.get('description'):
                    print(f"     描述: {entity['description'][:100]}...")
        
        # 显示关系
        relationships = entities_result.get('relationships', [])
        if relationships:
            print(f"\n前3个关系示例:")
            for i, rel in enumerate(relationships[:3]):
                print(f"  {i+1}. {rel.get('from', 'N/A')} -> {rel.get('to', 'N/A')} ({rel.get('relation', 'N/A')})")
        
        # 显示文档分析
        doc_analysis = entities_result.get('document_analysis', {})
        if doc_analysis:
            print(f"\n文档分析结果:")
            doc_info = doc_analysis.get('document_info', {})
            if doc_info:
                print(f"  文档类型: {doc_info.get('type', 'N/A')}")
                print(f"  文档领域: {doc_info.get('domain', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 实体提取测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_parse_and_extract_entities():
    """测试文档解析和实体提取一体化功能"""
    print("\n=== 测试文档解析 + 实体提取一体化功能 ===\n")
    
    # 检查是否有示例PDF文件
    pdf_file = Path("../input/p5-14.pdf")
    if not pdf_file.exists():
        pdf_file = Path("./input/p5-14.pdf")
    
    if pdf_file.exists():
        print(f"发现PDF文件: {pdf_file}")
        
        # 初始化RAG-CL系统
        config = RAGAnythingCLConfig(
            parser="mineru",
            working_dir="./output",
            save_intermediate=True
        )
        ragcl = RAGAnythingCL(config)
        
        try:
            # 检查安装
            if not ragcl.check_installation():
                print("⚠️  MinerU安装检查失败，跳过实际处理")
                return False
            
            print("\n开始文档解析和实体提取...")
            complete_result = ragcl.parse_and_extract_entities(
                pdf_file,
                extract_relations=True
            )
            
            # 显示结果摘要
            print(f"\n✅ 完整处理完成!")
            
            parsing_stats = complete_result['parsing_stats']
            print(f"\n解析统计:")
            print(f"  总内容块数: {parsing_stats['total_content_blocks']}")
            print(f"  内容类型分布: {parsing_stats['content_types']}")
            
            entity_stats = complete_result['entity_stats']
            print(f"\n实体提取统计:")
            print(f"  提取实体数: {entity_stats['total_entities']}")
            print(f"  提取关系数: {entity_stats['total_relationships']}")
            print(f"  处理文本块: {entity_stats.get('text_blocks_processed', 0)}")
            print(f"  处理表格块: {entity_stats.get('table_blocks_processed', 0)}")
            
            # 显示实体示例
            entities = complete_result.get('entities', [])
            if entities:
                print(f"\n实体示例:")
                for i, entity in enumerate(entities[:3]):
                    print(f"  {i+1}. {entity.get('name', 'N/A')} ({entity.get('type', 'N/A')})")
                    source_info = f"来源: 页面{entity.get('source_page', 0)} - {entity.get('source_type', 'unknown')}"
                    print(f"     {source_info}")
            
            return True
            
        except Exception as e:
            print(f"❌ 完整处理测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    else:
        print("⚠️  未找到PDF文件，跳过文档解析测试")
        return False


def test_entity_extractor_directly():
    """直接测试EntityExtractor类"""
    print("\n=== 直接测试EntityExtractor类 ===\n")
    
    from ragcl import EntityExtractor
    
    # 创建实体提取器
    extractor = EntityExtractor()
    
    # 简单的测试内容
    test_content = [
        {
            "type": "text",
            "text": "Python是一种高级编程语言，广泛应用于机器学习和数据分析领域。TensorFlow和PyTorch是两个主要的深度学习框架。",
            "page_idx": 0
        }
    ]
    
    try:
        print("测试同步实体提取...")
        result = extractor.extract_entities_sync(test_content)
        
        print(f"✅ 直接测试成功!")
        print(f"提取统计: {result.get('statistics', {})}")
        
        entities = result.get('entities', [])
        if entities:
            print(f"提取的实体:")
            for entity in entities:
                print(f"  - {entity.get('name', 'N/A')} ({entity.get('type', 'N/A')})")
        
        return True
        
    except Exception as e:
        print(f"❌ 直接测试失败: {str(e)}")
        print("这可能是因为API配置问题或网络连接问题")
        return False


def demonstrate_api_configuration():
    """演示API配置选项"""
    print("\n=== API配置选项演示 ===\n")
    
    from ragcl import EntityExtractor
    
    print("EntityExtractor支持以下配置选项:")
    print("1. api_base: LLM API基础URL")
    print("2. api_key: API密钥")
    print("3. model: 使用的模型名称")
    
    print(f"\n当前默认配置:")
    print(f"  API Base: https://api.chatanywhere.tech/v1")
    print(f"  Model: gpt-3.5-turbo")
    print(f"  API Key: sk-FiF5mSQ5EF1QrvI4FrVB7ZnrmXCjlJDUokJfTJ7HuNP5KQ78")
    
    print(f"\n自定义配置示例:")
    print("""
    extractor = EntityExtractor(
        api_base="https://your-api-url.com/v1",
        api_key="your-api-key",
        model="gpt-4"
    )
    """)


if __name__ == "__main__":
    print("=== RAG-CL实体提取功能测试 ===\n")
    
    # 测试序列
    tests = [
        ("模拟内容实体提取", test_entity_extraction_with_parsed_content),
        ("文档解析+实体提取", test_parse_and_extract_entities),
        ("EntityExtractor直接测试", test_entity_extractor_directly),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"运行测试: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 异常: {str(e)}")
            results[test_name] = False
    
    # 显示API配置信息
    demonstrate_api_configuration()
    
    # 测试总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    print(f"\n总体结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过! 实体提取功能已成功集成到RAG-CL系统中。")
    else:
        print("⚠️  部分测试失败。请检查:")
        print("   1. LLM API配置是否正确")
        print("   2. 网络连接是否正常")
        print("   3. MinerU解析器是否正确安装")
    
    print(f"\n输出文件保存在: ./output/")
    print(f"更多信息请查看日志输出。")