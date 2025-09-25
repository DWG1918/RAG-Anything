#!/usr/bin/env python3
"""
快速实体提取测试

使用解析后内容的一小部分进行快速测试
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import logging
from ragcl import RAGAnythingCL, RAGAnythingCLConfig

# 设置日志级别为WARNING以减少输出
logging.basicConfig(level=logging.WARNING)


def main():
    print("=== 快速实体提取测试 (使用解析后内容) ===\n")
    
    # 加载解析后的内容
    parsed_files = [
        "quick_parse_output/p5-14_parsed.json",
        # "quick_parse_output/p5-14/auto/p5-14_content_list.json"
    ]
    
    content_list = None
    for file_path in parsed_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content_list = json.load(f)
                print(f"✅ 加载解析后内容: {file_path}")
                break
            except Exception as e:
                print(f"❌ 加载失败 {file_path}: {e}")
                continue
    
    if not content_list:
        print("❌ 未找到解析后内容文件")
        return
    
    print(f"📊 总内容块数: {len(content_list)}")
    
    # 分析内容类型
    content_types = {}
    for item in content_list:
        if isinstance(item, dict):
            content_type = item.get('type', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
    
    print("内容类型分布:", content_types)
    
    # 选择前15个有意义的内容块进行测试（跳过太短的文本）
    test_content = []
    for item in content_list:
        if isinstance(item, dict):
            content_type = item.get('type', '')
            
            if content_type == 'text':
                text = item.get('text', '').strip()
                if len(text) > 20:  # 只选择有足够内容的文本块
                    test_content.append(item)
            elif content_type in ['table', 'image']:
                test_content.append(item)
            
            if len(test_content) >= 15:  # 限制为15个块以加快测试
                break
    
    print(f"\n🎯 选择 {len(test_content)} 个内容块进行测试:")
    for i, item in enumerate(test_content):
        content_type = item.get('type', 'unknown')
        page_idx = item.get('page_idx', 0)
        
        if content_type == 'text':
            text = item.get('text', '')[:60]
            print(f"  {i+1}. [页面{page_idx}] 文本: \"{text}...\"")
        elif content_type == 'table':
            caption = item.get('table_caption', '无标题表格')
            print(f"  {i+1}. [页面{page_idx}] 表格: {caption}")
        elif content_type == 'image':
            caption = item.get('image_caption', '无标题图片')
            print(f"  {i+1}. [页面{page_idx}] 图片: {caption}")
    
    # 初始化RAG-CL并进行实体提取
    print(f"\n🚀 开始实体提取...")
    config = RAGAnythingCLConfig(working_dir="./extract_entities", save_intermediate=True)
    ragcl = RAGAnythingCL(config)
    
    try:
        result = ragcl.extract_entities(test_content, extract_relations=True)
        
        # 显示结果
        stats = result['statistics']
        print(f"\n✅ 实体提取完成!")
        print(f"📈 处理统计:")
        print(f"  - 处理文本块: {stats.get('text_blocks_processed', 0)}")
        print(f"  - 处理表格块: {stats.get('table_blocks_processed', 0)}")
        print(f"  - 提取实体数: {stats['total_entities']}")
        print(f"  - 提取关系数: {stats['total_relationships']}")
        
        # 显示实体
        entities = result.get('entities', [])
        if entities:
            print(f"\n🏷️  提取的实体:")
            for i, entity in enumerate(entities, 1):
                name = entity.get('name', 'N/A')
                entity_type = entity.get('type', 'N/A')
                source_page = entity.get('source_page', 'N/A')
                
                print(f"  {i:2d}. {name} ({entity_type}) - 页面{source_page}")
                
                description = entity.get('description', '')
                if description:
                    print(f"      {description[:100]}...")
        
        # 显示关系
        relationships = result.get('relationships', [])
        if relationships:
            print(f"\n🔗 实体关系:")
            for i, rel in enumerate(relationships, 1):
                from_entity = rel.get('from', 'N/A')
                to_entity = rel.get('to', 'N/A')
                relation = rel.get('relation', 'N/A')
                
                print(f"  {i}. {from_entity} --[{relation}]--> {to_entity}")
        
        # 显示文档分析
        doc_analysis = result.get('document_analysis', {})
        if doc_analysis:
            print(f"\n📄 文档分析:")
            doc_info = doc_analysis.get('document_info', {})
            if doc_info:
                print(f"  类型: {doc_info.get('type', 'N/A')}")
                print(f"  领域: {doc_info.get('domain', 'N/A')}")
                print(f"  语言: {doc_info.get('language', 'N/A')}")
        
        print(f"\n🎉 测试完成! 实体提取功能在解析后内容上运行正常。")
        print(f"💾 详细结果已保存到: ./output/ 目录")
        
    except Exception as e:
        print(f"❌ 实体提取失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()