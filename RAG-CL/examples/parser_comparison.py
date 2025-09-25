#!/usr/bin/env python3
"""
RAG-CL解析器对比示例

This example compares MinerU and Docling parsers performance and capabilities.
"""

import logging
import time
from pathlib import Path
from ragcl import RAGAnythingCL, RAGAnythingCLConfig

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compare_parsers(file_path: str):
    """
    对比MinerU和Docling解析器
    
    Args:
        file_path: 要解析的文件路径
    """
    print(f"\n=== 解析器对比: {file_path} ===")
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    parsers = ["mineru", "docling"]
    results = {}
    
    for parser_name in parsers:
        print(f"\n--- 使用 {parser_name} 解析器 ---")
        
        try:
            # 创建配置
            config = RAGAnythingCLConfig(
                parser=parser_name,
                working_dir=f"./output_{parser_name}",
                enable_image_processing=True,
                enable_table_processing=True,
                enable_equation_processing=True
            )
            
            # 初始化RAG-CL
            ragcl = RAGAnythingCL(config)
            
            # 检查安装
            if not ragcl.check_installation():
                print(f"❌ {parser_name} 未正确安装，跳过")
                results[parser_name] = {"error": "not_installed"}
                continue
            
            # 记录开始时间
            start_time = time.time()
            
            # 解析文档
            content_list = ragcl.parse_document(file_path)
            
            # 记录结束时间
            end_time = time.time()
            processing_time = end_time - start_time
            
            # 统计结果
            content_stats = {}
            for item in content_list:
                if isinstance(item, dict):
                    content_type = item.get("type", "unknown")
                    content_stats[content_type] = content_stats.get(content_type, 0) + 1
            
            results[parser_name] = {
                "success": True,
                "content_blocks": len(content_list),
                "content_types": content_stats,
                "processing_time": processing_time,
                "supported_formats": ragcl.get_supported_formats()
            }
            
            print(f"✅ 解析成功")
            print(f"⏱️  处理时间: {processing_time:.2f}秒")
            print(f"📊 内容块总数: {len(content_list)}")
            print(f"📋 内容类型分布: {content_stats}")
            
        except Exception as e:
            print(f"❌ 解析失败: {str(e)}")
            results[parser_name] = {"error": str(e)}
    
    # 对比结果
    print(f"\n=== 对比结果 ===")
    
    # 创建对比表格
    print("| 解析器 | 状态 | 内容块数 | 处理时间 | 主要内容类型 |")
    print("|--------|------|----------|----------|--------------|")
    
    for parser_name, result in results.items():
        if "error" in result:
            status = f"❌ {result['error']}"
            blocks = "-"
            time_str = "-"
            types = "-"
        else:
            status = "✅ 成功"
            blocks = str(result["content_blocks"])
            time_str = f"{result['processing_time']:.2f}s"
            types = ", ".join(f"{k}({v})" for k, v in result["content_types"].items())
        
        print(f"| {parser_name} | {status} | {blocks} | {time_str} | {types} |")
    
    # 推荐使用场景
    print(f"\n=== 推荐使用场景 ===")
    print("MinerU 适用于:")
    print("  ✓ PDF文档的精确解析")  
    print("  ✓ 图片和扫描文档的OCR")
    print("  ✓ 复杂版式的学术论文")
    print("  ✓ 需要公式和表格识别")
    
    print("\nDocling 适用于:")
    print("  ✓ Office文档的原生解析")
    print("  ✓ HTML网页内容提取")
    print("  ✓ 结构化文档处理")
    print("  ✓ 快速批量处理")


def test_format_support():
    """测试不同格式支持情况"""
    print("\n=== 格式支持对比 ===")
    
    parsers = ["mineru", "docling"]
    
    for parser_name in parsers:
        try:
            config = RAGAnythingCLConfig(parser=parser_name)
            ragcl = RAGAnythingCL(config)
            
            if not ragcl.check_installation():
                print(f"❌ {parser_name} 未安装")
                continue
            
            print(f"\n{parser_name.upper()} 支持的格式:")
            formats = ragcl.get_supported_formats()
            
            for category, extensions in formats.items():
                ext_list = ", ".join(extensions)
                print(f"  {category}: {ext_list}")
                
        except Exception as e:
            print(f"❌ {parser_name} 初始化失败: {str(e)}")


def benchmark_performance(file_paths: list):
    """性能基准测试"""
    print("\n=== 性能基准测试 ===")
    
    if not file_paths:
        print("❌ 未提供测试文件")
        return
    
    existing_files = [f for f in file_paths if Path(f).exists()]
    if not existing_files:
        print("❌ 未找到有效的测试文件")
        return
    
    print(f"测试文件: {existing_files}")
    
    parsers = ["mineru", "docling"]
    performance_data = {}
    
    for parser_name in parsers:
        try:
            config = RAGAnythingCLConfig(
                parser=parser_name,
                working_dir=f"./benchmark_{parser_name}",
                batch_size=len(existing_files),
                max_workers=2
            )
            ragcl = RAGAnythingCL(config)
            
            if not ragcl.check_installation():
                print(f"⚠️  {parser_name} 未安装，跳过性能测试")
                continue
            
            print(f"\n--- {parser_name} 批量处理性能 ---")
            
            start_time = time.time()
            results = ragcl.parse_documents_batch(existing_files)
            end_time = time.time()
            
            total_time = end_time - start_time
            successful_files = len(results)
            total_blocks = sum(len(content) for content in results.values())
            
            performance_data[parser_name] = {
                "total_time": total_time,
                "successful_files": successful_files,
                "total_blocks": total_blocks,
                "avg_time_per_file": total_time / max(successful_files, 1),
                "blocks_per_second": total_blocks / total_time if total_time > 0 else 0
            }
            
            print(f"  总处理时间: {total_time:.2f}秒")
            print(f"  成功文件数: {successful_files}/{len(existing_files)}")
            print(f"  总内容块数: {total_blocks}")
            print(f"  平均每文件: {total_time/max(successful_files, 1):.2f}秒")
            print(f"  处理速度: {total_blocks/total_time:.1f} 块/秒" if total_time > 0 else "  处理速度: N/A")
            
        except Exception as e:
            print(f"❌ {parser_name} 性能测试失败: {str(e)}")
    
    # 性能对比总结
    if len(performance_data) > 1:
        print(f"\n=== 性能对比总结 ===")
        fastest_parser = min(performance_data.keys(), 
                           key=lambda x: performance_data[x]["avg_time_per_file"])
        print(f"🏃 最快解析器: {fastest_parser}")
        
        most_efficient = max(performance_data.keys(),
                           key=lambda x: performance_data[x]["blocks_per_second"])
        print(f"⚡ 最高效率: {most_efficient}")


def main():
    """主函数"""
    print("=== RAG-CL 解析器对比工具 ===")
    
    # 示例文件列表 - 请替换为实际文件路径
    test_files = [
        "example.pdf",
        "document.docx",
        "presentation.pptx",
        "spreadsheet.xlsx",
        "webpage.html"
    ]
    
    # 1. 测试格式支持
    test_format_support()
    
    # 2. 单文件对比
    existing_files = [f for f in test_files if Path(f).exists()]
    if existing_files:
        for file_path in existing_files[:2]:  # 只测试前两个文件
            compare_parsers(file_path)
    else:
        print("\n⚠️  未找到测试文件，请将以下文件放置在当前目录:")
        for f in test_files:
            print(f"  - {f}")
    
    # 3. 性能基准测试
    benchmark_performance(existing_files)
    
    print(f"\n=== 总结与建议 ===")
    print("选择解析器的建议:")
    print("1. 🔍 主要处理PDF和图片 → 选择 MinerU")
    print("2. 📄 主要处理Office文档 → 选择 Docling")
    print("3. 🌐 需要处理HTML内容 → 选择 Docling")
    print("4. ⚡ 追求处理速度 → 根据基准测试结果选择")
    print("5. 🎯 需要高精度OCR → 选择 MinerU")


if __name__ == "__main__":
    main()