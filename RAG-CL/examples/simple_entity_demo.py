#!/usr/bin/env python3
"""
Simple Entity Extraction Demo

Demonstrates the basic entity extraction functionality of RAG-CL.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from ragcl import RAGAnythingCL, RAGAnythingCLConfig

# 设置日志级别为WARNING以减少输出
logging.basicConfig(level=logging.WARNING)

def main():
    print("=== RAG-CL 实体提取功能演示 ===\n")
    
    # 创建示例文档内容
    sample_content = [
        {
            "type": "text",
            "text": "深度学习是机器学习的一个子领域，使用人工神经网络进行学习。卷积神经网络(CNN)在图像识别任务中表现出色。",
            "page_idx": 0,
            "block_index": 0
        },
        {
            "type": "text",
            "text": "ResNet-50是微软研究院开发的残差网络架构，在ImageNet数据集上取得了优异的性能。该模型有约2560万个参数。",
            "page_idx": 0,
            "block_index": 1
        },
        {
            "type": "table",
            "table_caption": "深度学习模型对比",
            "table_body": [
                ["模型", "准确率", "参数量"],
                ["ResNet-50", "76.15%", "25.6M"],
                ["VGG-16", "71.59%", "138M"]
            ],
            "page_idx": 1,
            "block_index": 2
        }
    ]
    
    print(f"示例文档包含 {len(sample_content)} 个内容块")
    print("- 2个文本块")
    print("- 1个表格块")
    
    # 初始化RAG-CL
    print(f"\n初始化RAG-CL系统...")
    config = RAGAnythingCLConfig(
        working_dir="./output",
        save_intermediate=True
    )
    ragcl = RAGAnythingCL(config)
    
    # 执行实体提取
    print(f"\n开始实体提取...")
    try:
        result = ragcl.extract_entities(sample_content, extract_relations=True)
        
        # 显示统计信息
        stats = result['statistics']
        print(f"\n✅ 实体提取完成!")
        print(f"   - 处理文本块: {stats['text_blocks_processed']}")
        print(f"   - 处理表格块: {stats['table_blocks_processed']}")
        print(f"   - 提取实体数: {stats['total_entities']}")
        print(f"   - 提取关系数: {stats['total_relationships']}")
        
        # 显示提取的实体
        entities = result.get('entities', [])
        if entities:
            print(f"\n📋 提取的实体:")
            for i, entity in enumerate(entities, 1):
                name = entity.get('name', 'N/A')
                entity_type = entity.get('type', 'N/A')
                description = entity.get('description', '')
                
                print(f"   {i}. {name} ({entity_type})")
                if description:
                    print(f"      描述: {description[:80]}...")
        
        # 显示实体关系
        relationships = result.get('relationships', [])
        if relationships:
            print(f"\n🔗 实体关系:")
            for i, rel in enumerate(relationships, 1):
                from_entity = rel.get('from', 'N/A')
                to_entity = rel.get('to', 'N/A')
                relation = rel.get('relation', 'N/A')
                
                print(f"   {i}. {from_entity} --{relation}--> {to_entity}")
        
        # 显示文档分析结果
        doc_analysis = result.get('document_analysis', {})
        if doc_analysis:
            print(f"\n📄 文档分析:")
            doc_info = doc_analysis.get('document_info', {})
            if doc_info:
                print(f"   文档类型: {doc_info.get('type', 'N/A')}")
                print(f"   领域: {doc_info.get('domain', 'N/A')}")
                print(f"   语言: {doc_info.get('language', 'N/A')}")
        
        print(f"\n🎉 演示完成!")
        print(f"实体提取功能已成功集成到RAG-CL系统中。")
        
    except Exception as e:
        print(f"❌ 实体提取失败: {str(e)}")
        print("请检查API配置和网络连接。")


if __name__ == "__main__":
    main()