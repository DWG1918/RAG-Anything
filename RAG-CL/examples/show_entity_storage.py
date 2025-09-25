#!/usr/bin/env python3
"""
展示实体提取结果的保存位置和格式

演示RAG-CL系统中实体提取结果的存储机制
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import logging
from ragcl import RAGAnythingCL, RAGAnythingCLConfig

# 设置日志级别
logging.basicConfig(level=logging.WARNING)


def demonstrate_entity_storage():
    """演示实体提取结果存储"""
    
    print("=== RAG-CL 实体提取结果存储演示 ===\n")
    
    # 创建一个简单的示例内容
    sample_content = [
        {
            "type": "text",
            "text": "西门子公司开发了一套标准化的声学包装解决方案。该产品包括通风系统、消音器和管道工程等组件。",
            "page_idx": 0,
            "block_index": 0
        },
        {
            "type": "table", 
            "table_caption": "设备规格表",
            "table_body": [
                ["设备名称", "型号", "功率"],
                ["风机", "SGT-100", "500W"],
                ["消音器", "AS-200", "N/A"]
            ],
            "page_idx": 1,
            "block_index": 1
        }
    ]
    
    print("📝 示例文档内容:")
    for i, item in enumerate(sample_content, 1):
        content_type = item.get('type', 'unknown')
        if content_type == 'text':
            print(f"  {i}. 文本: \"{item.get('text', '')[:50]}...\"")
        elif content_type == 'table':
            caption = item.get('table_caption', '无标题')
            print(f"  {i}. 表格: {caption}")
    
    # 配置RAG-CL系统，启用结果保存
    print(f"\n⚙️  配置RAG-CL系统:")
    config = RAGAnythingCLConfig(
        working_dir="./demo_output",  # 指定输出目录
        save_intermediate=True        # 启用结果保存
    )
    print(f"  • 输出目录: {config.working_dir}")
    print(f"  • 保存中间结果: {config.save_intermediate}")
    
    ragcl = RAGAnythingCL(config)
    
    # 执行实体提取
    print(f"\n🚀 执行实体提取...")
    try:
        result = ragcl.extract_entities(sample_content, extract_relations=True)
        
        # 显示提取统计
        stats = result['statistics']
        print(f"✅ 实体提取完成:")
        print(f"  • 提取实体数: {stats['total_entities']}")
        print(f"  • 提取关系数: {stats['total_relationships']}")
        
        # 检查保存的文件
        output_dir = Path("demo_output")
        print(f"\n📁 检查输出目录: {output_dir.absolute()}")
        
        if output_dir.exists():
            saved_files = list(output_dir.glob("*.json"))
            if saved_files:
                print(f"✅ 找到 {len(saved_files)} 个保存的文件:")
                for file_path in saved_files:
                    file_size = file_path.stat().st_size
                    print(f"  📄 {file_path.name} ({file_size} bytes)")
            else:
                print(f"⚠️  输出目录存在但未找到JSON文件")
        else:
            print(f"⚠️  输出目录不存在")
        
    except Exception as e:
        print(f"❌ 实体提取失败: {e}")
        return


def show_storage_structure():
    """显示存储结构和文件格式"""
    
    print(f"\n{'='*60}")
    print("📋 RAG-CL 实体存储结构说明")
    print(f"{'='*60}")
    
    storage_info = {
        "默认存储位置": "./output/",
        "可配置目录": "通过 RAGAnythingCLConfig(working_dir='自定义路径')",
        "保存条件": "config.save_intermediate = True",
        "文件命名规则": {
            "完整结果": "{文档名}_complete_results.json", 
            "实体结果": "{文档名}_entities.json",
            "解析结果": "{文档名}_parsed.json"
        }
    }
    
    print(f"🗂️  存储配置:")
    for key, value in storage_info.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    • {k}: {v}")
        else:
            print(f"  • {key}: {value}")
    
    print(f"\n📄 实体文件结构示例:")
    entity_structure = {
        "entities": [
            {
                "name": "实体名称",
                "type": "实体类型",
                "description": "实体描述",
                "relevance_score": "相关性评分",
                "source_page": "来源页面",
                "source_type": "来源类型"
            }
        ],
        "relationships": [
            {
                "from": "源实体",
                "to": "目标实体", 
                "relation": "关系类型",
                "description": "关系描述",
                "confidence": "置信度"
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
            "total_entities": "实体总数",
            "total_relationships": "关系总数",
            "text_blocks_processed": "处理文本块数",
            "table_blocks_processed": "处理表格块数"
        }
    }
    
    print(json.dumps(entity_structure, ensure_ascii=False, indent=2))


def show_access_methods():
    """展示访问保存结果的方法"""
    
    print(f"\n{'='*60}")
    print("🔍 访问保存的实体结果")
    print(f"{'='*60}")
    
    print(f"💡 编程方式访问:")
    access_code = '''
import json
from pathlib import Path

# 加载实体提取结果
entities_file = "output/document_entities.json"
if Path(entities_file).exists():
    with open(entities_file, 'r', encoding='utf-8') as f:
        entities_data = json.load(f)
    
    # 访问实体列表
    entities = entities_data['entities']
    for entity in entities:
        print(f"实体: {entity['name']} ({entity['type']})")
    
    # 访问关系列表  
    relationships = entities_data['relationships']
    for rel in relationships:
        print(f"关系: {rel['from']} -> {rel['to']}")
'''
    print(access_code)
    
    print(f"🔨 命令行方式访问:")
    cli_commands = [
        "# 查看所有保存的文件",
        "ls -la output/",
        "",
        "# 查看实体文件内容", 
        "cat output/document_entities.json | jq '.entities'",
        "",
        "# 统计实体数量",
        "cat output/document_entities.json | jq '.statistics'",
        "",
        "# 查看文档分析结果",
        "cat output/document_entities.json | jq '.document_analysis'"
    ]
    
    for cmd in cli_commands:
        print(f"  {cmd}")


if __name__ == "__main__":
    # 演示实体存储
    demonstrate_entity_storage()
    
    # 显示存储结构
    show_storage_structure() 
    
    # 显示访问方法
    show_access_methods()
    
    print(f"\n{'='*60}")
    print("📝 总结")
    print(f"{'='*60}")
    
    print("RAG-CL系统实体提取结果保存位置:")
    print("✅ 默认位置: ./output/ 目录")  
    print("✅ 可自定义: 通过working_dir参数指定")
    print("✅ 文件格式: JSON格式，支持中文")
    print("✅ 保存条件: save_intermediate=True")
    print("✅ 文件类型:")
    print("   • {文档名}_entities.json - 仅实体和关系数据") 
    print("   • {文档名}_complete_results.json - 包含解析和实体的完整结果")
    print("   • {文档名}_parsed.json - 仅文档解析结果")
    
    print(f"\n💡 使用建议:")
    print("• 生产环境建议使用绝对路径指定输出目录")
    print("• 大量文档处理时注意磁盘空间管理") 
    print("• 可使用jq工具进行JSON数据查询和分析")