#!/usr/bin/env python3
"""
实际演示实体提取结果保存

使用parse_and_extract_entities方法展示完整的保存过程
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import logging
from ragcl import RAGAnythingCL, RAGAnythingCLConfig

logging.basicConfig(level=logging.WARNING)


def create_mock_document():
    """创建模拟文档内容进行测试"""
    mock_content = [
        {
            "type": "text",
            "text": "本技术规格说明了Siemens SGT-100燃气轮机的声学包装系统。该系统包括隔音外壳、通风系统和排气消声器等关键组件。",
            "page_idx": 0,
            "block_index": 0
        },
        {
            "type": "text", 
            "text": "声学包装的主要目标是将噪声降低到环境标准要求的水平。系统采用多层隔音材料和先进的消声技术。",
            "page_idx": 0,
            "block_index": 1
        },
        {
            "type": "table",
            "table_caption": "噪声控制规格",
            "table_body": [
                ["组件", "噪声等级", "标准"],
                ["燃气轮机", "85 dB", "ISO 3744"],
                ["通风系统", "70 dB", "ISO 9614"],
                ["排气系统", "90 dB", "ISO 3746"]
            ],
            "page_idx": 1,
            "block_index": 2
        }
    ]
    return mock_content


def demonstrate_entity_saving():
    """演示实体提取和保存过程"""
    
    print("=== 实体提取结果保存演示 ===\n")
    
    # 创建配置，指定保存位置
    output_dir = "./entity_results"
    config = RAGAnythingCLConfig(
        working_dir=output_dir,
        save_intermediate=True,
        output_format="json"
    )
    
    print(f"📁 配置输出目录: {Path(output_dir).absolute()}")
    
    # 初始化系统
    ragcl = RAGAnythingCL(config)
    
    # 获取模拟文档内容
    content_list = create_mock_document()
    print(f"📄 模拟文档包含 {len(content_list)} 个内容块")
    
    # 执行实体提取
    print(f"\n🚀 开始实体提取和保存...")
    
    try:
        # 使用extract_entities方法（只做实体提取，不涉及文件解析）
        result = ragcl.extract_entities(content_list, extract_relations=True)
        
        # 手动保存结果（模拟parse_and_extract_entities的保存逻辑）
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 保存实体结果
        entities_file = output_path / "demo_document_entities.json"
        entities_data = {
            "entities": result["entities"],
            "relationships": result["relationships"], 
            "document_analysis": result["document_analysis"],
            "statistics": result["statistics"]
        }
        
        with open(entities_file, 'w', encoding='utf-8') as f:
            json.dump(entities_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 实体提取完成!")
        print(f"📊 提取统计:")
        stats = result['statistics']
        print(f"  • 实体数量: {stats['total_entities']}")
        print(f"  • 关系数量: {stats['total_relationships']}")
        print(f"  • 处理文本块: {stats.get('text_blocks_processed', 0)}")
        print(f"  • 处理表格块: {stats.get('table_blocks_processed', 0)}")
        
        # 检查保存的文件
        print(f"\n💾 检查保存的文件:")
        if entities_file.exists():
            file_size = entities_file.stat().st_size
            print(f"✅ {entities_file.name} ({file_size} bytes)")
            
            # 读取并显示部分内容
            with open(entities_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            print(f"\n📋 保存的实体示例 (前5个):")
            entities = saved_data.get('entities', [])
            for i, entity in enumerate(entities[:5], 1):
                name = entity.get('name', 'N/A')
                entity_type = entity.get('type', 'N/A')
                print(f"  {i}. {name} ({entity_type})")
            
            print(f"\n🔗 保存的关系示例 (前3个):")
            relationships = saved_data.get('relationships', [])
            for i, rel in enumerate(relationships[:3], 1):
                from_entity = rel.get('from', 'N/A')
                to_entity = rel.get('to', 'N/A') 
                relation = rel.get('relation', 'N/A')
                print(f"  {i}. {from_entity} --[{relation}]--> {to_entity}")
            
            print(f"\n📈 保存的统计信息:")
            statistics = saved_data.get('statistics', {})
            for key, value in statistics.items():
                print(f"  • {key}: {value}")
        else:
            print(f"❌ 文件保存失败")
        
        return entities_file
        
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def show_file_access_examples(entities_file):
    """展示文件访问示例"""
    
    if not entities_file or not entities_file.exists():
        return
        
    print(f"\n{'='*50}")
    print("🔍 文件访问示例")
    print(f"{'='*50}")
    
    print(f"📂 文件路径: {entities_file.absolute()}")
    
    # Python访问示例
    print(f"\n💻 Python访问代码:")
    python_code = f'''
import json

# 加载实体数据
with open("{entities_file}", "r", encoding="utf-8") as f:
    data = json.load(f)

# 获取所有实体
entities = data["entities"]
print(f"共有 {{len(entities)}} 个实体")

# 获取所有关系
relationships = data["relationships"]
print(f"共有 {{len(relationships)}} 个关系")

# 获取统计信息
stats = data["statistics"]
print(f"统计信息: {{stats}}")
'''
    print(python_code)
    
    # 命令行访问示例
    print(f"🖥️  命令行访问:")
    print(f"  # 查看文件内容")
    print(f"  cat {entities_file}")
    print(f"")
    print(f"  # 使用jq查看实体 (需要安装jq)")
    print(f"  cat {entities_file} | jq '.entities[0:3]'")
    print(f"")
    print(f"  # 统计实体数量")
    print(f"  cat {entities_file} | jq '.entities | length'")


if __name__ == "__main__":
    # 演示保存过程
    saved_file = demonstrate_entity_saving()
    
    # 展示访问方法
    if saved_file:
        show_file_access_examples(saved_file)
    
    print(f"\n{'='*60}")
    print("📝 总结")
    print(f"{'='*60}")
    
    print("RAG-CL实体提取结果保存机制:")
    print("✅ 自动保存: 当save_intermediate=True时自动保存")
    print("✅ 文件位置: working_dir指定的目录")
    print("✅ 文件格式: UTF-8编码的JSON文件")
    print("✅ 文件内容: 包含entities、relationships、document_analysis、statistics")
    print("✅ 访问方式: Python json库或命令行工具")
    
    print(f"\n💡 保存文件的具体位置取决于:")
    print("1. RAGAnythingCLConfig的working_dir参数")
    print("2. save_intermediate参数必须为True")
    print("3. 使用parse_and_extract_entities()会自动保存")
    print("4. 使用extract_entities()需要手动保存")