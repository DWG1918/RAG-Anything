#!/usr/bin/env python3
"""
修复实体提取结果保存问题

演示正确的实体提取和保存方法
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import logging
from ragcl import RAGAnythingCL, RAGAnythingCLConfig

logging.basicConfig(level=logging.WARNING)


def load_parsed_content():
    """加载解析后的内容"""
    parsed_files = [
        "quick_parse_output/p5-14_parsed.json",
        "quick_parse_output/p5-14/auto/p5-14_content_list.json"
    ]
    
    for file_path in parsed_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content_list = json.load(f)
                print(f"✅ 加载解析后内容: {file_path}")
                return content_list
            except Exception as e:
                print(f"❌ 加载失败 {file_path}: {e}")
                continue
    
    return None


def method1_extract_entities_with_manual_save():
    """方法1: 使用extract_entities()并手动保存结果"""
    print("=== 方法1: extract_entities() + 手动保存 ===\n")
    
    # 加载内容
    content_list = load_parsed_content()
    if not content_list:
        print("❌ 未找到解析后内容")
        return
    
    # 选择前10个内容块
    test_content = []
    for item in content_list:
        if isinstance(item, dict):
            content_type = item.get('type', '')
            if content_type == 'text' and len(item.get('text', '').strip()) > 20:
                test_content.append(item)
            elif content_type in ['table', 'image']:
                test_content.append(item)
            if len(test_content) >= 10:
                break
    
    print(f"📄 处理 {len(test_content)} 个内容块")
    
    # 配置RAG-CL
    config = RAGAnythingCLConfig(
        working_dir="./method1_output",
        save_intermediate=True
    )
    ragcl = RAGAnythingCL(config)
    
    try:
        # 执行实体提取
        result = ragcl.extract_entities(test_content, extract_relations=True)
        
        # 手动保存结果
        output_dir = Path("method1_output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        entities_file = output_dir / "extracted_entities.json"
        entities_data = {
            "entities": result["entities"],
            "relationships": result["relationships"],
            "document_analysis": result["document_analysis"],
            "statistics": result["statistics"]
        }
        
        with open(entities_file, 'w', encoding='utf-8') as f:
            json.dump(entities_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 实体提取完成并手动保存")
        print(f"📁 保存位置: {entities_file.absolute()}")
        print(f"📊 统计: {result['statistics']['total_entities']}个实体, {result['statistics']['total_relationships']}个关系")
        
        # 验证文件
        if entities_file.exists():
            file_size = entities_file.stat().st_size
            print(f"💾 文件大小: {file_size} bytes")
            return entities_file
        
    except Exception as e:
        print(f"❌ 方法1失败: {str(e)}")
        return None


def method2_parse_and_extract_with_auto_save():
    """方法2: 使用parse_and_extract_entities()自动保存"""
    print("\n=== 方法2: parse_and_extract_entities() + 自动保存 ===\n")
    
    # 检查是否有PDF文件
    pdf_file = None
    pdf_paths = [
        "input/p5-14.pdf",
        "../input/p5-14.pdf",
        "quick_parse_output/p5-14/auto/p5-14_origin.pdf"
    ]
    
    for path in pdf_paths:
        if Path(path).exists():
            pdf_file = Path(path)
            break
    
    if not pdf_file:
        print("⚠️  未找到PDF文件，跳过方法2")
        return None
    
    print(f"📄 发现PDF文件: {pdf_file}")
    
    # 配置RAG-CL
    config = RAGAnythingCLConfig(
        working_dir="./method2_output",
        save_intermediate=True,
        parser="mineru"
    )
    ragcl = RAGAnythingCL(config)
    
    # 检查解析器安装
    if not ragcl.check_installation():
        print("⚠️  MinerU未正确安装，跳过方法2")
        return None
    
    try:
        # 一体化处理（自动保存）
        print("🚀 开始文档解析和实体提取...")
        result = ragcl.parse_and_extract_entities(pdf_file, extract_relations=True)
        
        print(f"✅ 一体化处理完成并自动保存")
        
        # 检查生成的文件
        output_dir = Path("method2_output")
        saved_files = list(output_dir.glob("*.json"))
        
        if saved_files:
            print(f"📁 自动保存的文件:")
            for file_path in saved_files:
                file_size = file_path.stat().st_size
                print(f"  💾 {file_path.name} ({file_size} bytes)")
            
            # 返回实体文件
            entities_files = [f for f in saved_files if 'entities' in f.name]
            return entities_files[0] if entities_files else saved_files[0]
        
    except Exception as e:
        print(f"❌ 方法2失败: {str(e)}")
        return None


def method3_simulate_content_with_auto_save():
    """方法3: 使用已解析内容模拟parse_and_extract_entities()"""
    print("\n=== 方法3: 模拟parse_and_extract_entities()保存机制 ===\n")
    
    # 加载内容
    content_list = load_parsed_content()
    if not content_list:
        print("❌ 未找到解析后内容")
        return
    
    # 配置RAG-CL
    config = RAGAnythingCLConfig(
        working_dir="./method3_output",
        save_intermediate=True
    )
    ragcl = RAGAnythingCL(config)
    
    # 选择内容子集
    test_content = content_list[:15]  # 前15个块
    
    try:
        # 执行实体提取
        result = ragcl.extract_entities(test_content, extract_relations=True)
        
        # 模拟parse_and_extract_entities的保存逻辑
        output_dir = Path("method3_output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建完整结果（模拟parse_and_extract_entities的输出）
        complete_result = {
            "file_path": "parsed_content_simulation",
            "parsing_stats": {
                "total_content_blocks": len(test_content),
                "content_types": ragcl._get_content_type_stats(test_content)
            },
            "content_list": test_content,
            "entities": result["entities"],
            "relationships": result["relationships"],
            "document_analysis": result["document_analysis"],
            "entity_stats": result["statistics"]
        }
        
        # 保存完整结果
        complete_file = output_dir / "p5-14_complete_results.json"
        with open(complete_file, 'w', encoding='utf-8') as f:
            json.dump(complete_result, f, ensure_ascii=False, indent=2)
        
        # 保存实体结果
        entities_file = output_dir / "p5-14_entities.json"
        entities_data = {
            "entities": result["entities"],
            "relationships": result["relationships"],
            "document_analysis": result["document_analysis"],
            "statistics": result["statistics"]
        }
        
        with open(entities_file, 'w', encoding='utf-8') as f:
            json.dump(entities_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 模拟保存完成")
        print(f"📁 保存位置: {output_dir.absolute()}")
        print(f"📄 文件:")
        print(f"  • {complete_file.name} - 完整结果")
        print(f"  • {entities_file.name} - 实体结果")
        
        # 验证文件
        for file_path in [complete_file, entities_file]:
            if file_path.exists():
                file_size = file_path.stat().st_size
                print(f"💾 {file_path.name}: {file_size} bytes")
        
        return entities_file
        
    except Exception as e:
        print(f"❌ 方法3失败: {str(e)}")
        return None


def show_saved_files_content(entities_file):
    """显示保存文件的内容"""
    if not entities_file or not entities_file.exists():
        return
    
    print(f"\n📋 查看保存的实体文件内容:")
    print(f"文件: {entities_file.absolute()}")
    
    try:
        with open(entities_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 显示统计
        stats = data.get('statistics', {})
        print(f"\n📊 统计信息:")
        for key, value in stats.items():
            print(f"  • {key}: {value}")
        
        # 显示前几个实体
        entities = data.get('entities', [])
        print(f"\n🏷️  实体示例 (前5个):")
        for i, entity in enumerate(entities[:5], 1):
            name = entity.get('name', 'N/A')
            entity_type = entity.get('type', 'N/A')
            print(f"  {i}. {name} ({entity_type})")
        
        # 显示关系
        relationships = data.get('relationships', [])
        print(f"\n🔗 关系示例 (前3个):")
        for i, rel in enumerate(relationships[:3], 1):
            from_entity = rel.get('from', 'N/A')
            to_entity = rel.get('to', 'N/A')
            relation = rel.get('relation', 'N/A')
            print(f"  {i}. {from_entity} --[{relation}]--> {to_entity}")
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")


if __name__ == "__main__":
    print("=== 修复RAG-CL实体提取结果保存问题 ===\n")
    
    # 尝试三种方法
    methods = [
        ("方法1: extract_entities + 手动保存", method1_extract_entities_with_manual_save),
        ("方法2: parse_and_extract_entities自动保存", method2_parse_and_extract_with_auto_save),
        ("方法3: 模拟完整保存机制", method3_simulate_content_with_auto_save)
    ]
    
    successful_file = None
    
    for method_name, method_func in methods:
        print(f"\n{'='*50}")
        print(f"尝试 {method_name}")
        print(f"{'='*50}")
        
        try:
            result_file = method_func()
            if result_file and Path(result_file).exists():
                print(f"✅ {method_name} 成功")
                successful_file = result_file
                break
            else:
                print(f"⚠️  {method_name} 未生成文件")
        except Exception as e:
            print(f"❌ {method_name} 失败: {e}")
    
    # 显示最终结果
    print(f"\n{'='*60}")
    print("📝 问题解决方案总结")
    print(f"{'='*60}")
    
    if successful_file:
        print(f"✅ 成功保存实体提取结果!")
        show_saved_files_content(successful_file)
        
        print(f"\n💡 解决方法:")
        print("1. extract_entities()方法本身不自动保存文件")
        print("2. 需要手动保存结果或使用parse_and_extract_entities()")
        print("3. 确保save_intermediate=True且working_dir存在")
    else:
        print(f"❌ 所有方法都失败了")
        print("可能的问题:")
        print("• 缺少解析后的内容文件")
        print("• API配置问题")
        print("• 权限或路径问题")
    
    print(f"\n🎯 推荐使用方法:")
    print("• 对于新文档: ragcl.parse_and_extract_entities(file_path)")
    print("• 对于已解析内容: ragcl.extract_entities() + 手动保存")
    print("• 确保配置: save_intermediate=True")