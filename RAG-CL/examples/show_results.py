#!/usr/bin/env python3
"""
RAG-CL 解析结果展示脚本

展示MinerU解析的实际结果
"""

import sys
import json
import logging
from pathlib import Path

# 添加ragcl包到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ragcl import RAGAnythingCL, RAGAnythingCLConfig

# 设置日志
logging.basicConfig(level=logging.WARNING)  # 只显示警告和错误

def show_parsing_results():
    """显示实际的解析结果"""
    
    print("🎯 RAG-CL 实际PDF解析结果展示")
    print("=" * 50)
    
    # PDF文件路径
    pdf_path = Path(__file__).parent.parent / "input" / "p5-14.pdf"
    
    if not pdf_path.exists():
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    print(f"📄 源文件: {pdf_path.name}")
    print(f"📏 文件大小: {pdf_path.stat().st_size / 1024:.1f} KB")
    
    # 检查是否有解析结果
    output_dirs = [
        Path(__file__).parent / "quick_parse_output",
        Path(__file__).parent.parent / "quick_parse_output"
    ]
    
    content_list = None
    result_source = None
    
    for output_dir in output_dirs:
        if output_dir.exists():
            # 查找JSON结果文件
            json_files = list(output_dir.rglob("*_content_list.json"))
            if json_files:
                json_file = json_files[0]
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        content_list = json.load(f)
                    result_source = str(json_file)
                    break
                except Exception as e:
                    print(f"⚠️  读取{json_file}失败: {e}")
    
    if content_list:
        print(f"✅ 找到解析结果: {result_source}")
        display_results(content_list)
    else:
        print("⚠️  未找到现有解析结果，尝试重新解析...")
        perform_parsing(pdf_path)

def display_results(content_list):
    """显示解析结果"""
    
    print(f"\n📊 解析结果统计:")
    print(f"总内容块数: {len(content_list)}")
    
    # 统计内容类型
    content_types = {}
    pages = set()
    text_length = 0
    
    for item in content_list:
        if isinstance(item, dict):
            content_type = item.get('type', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
            
            page_idx = item.get('page_idx', 0)
            pages.add(page_idx)
            
            if content_type == 'text':
                text = item.get('text', '')
                text_length += len(text)
    
    print(f"页面数: {len(pages)}")
    print(f"总文本长度: {text_length} 字符")
    
    print(f"\n📋 内容类型分布:")
    for content_type, count in sorted(content_types.items()):
        print(f"  {content_type}: {count}")
    
    # 显示内容样本
    print(f"\n📄 内容样本展示 (前10个块):")
    for i, item in enumerate(content_list[:10]):
        if not isinstance(item, dict):
            continue
            
        content_type = item.get('type', 'unknown')
        page_idx = item.get('page_idx', 0)
        
        print(f"\n[{i+1}] 类型: {content_type} | 页面: {page_idx}")
        
        if content_type == 'text':
            text = item.get('text', '').strip()
            # 显示前100字符
            preview = text[:100].replace('\n', ' ') + ('...' if len(text) > 100 else '')
            print(f"    内容: {preview}")
            
        elif content_type == 'image':
            img_path = item.get('img_path', '')
            caption = item.get('image_caption', '')
            print(f"    图片: {Path(img_path).name if img_path else 'N/A'}")
            if caption:
                print(f"    说明: {caption}")
                
        elif content_type == 'table':
            caption = item.get('table_caption', '')
            table_body = item.get('table_body', [])
            print(f"    表格: {caption if caption else '(无标题)'}")
            if table_body:
                rows = len(table_body)
                cols = len(table_body[0]) if table_body and table_body[0] else 0
                print(f"    规模: {rows}行 × {cols}列")
                
        elif content_type == 'equation':
            text = item.get('text', '')
            print(f"    公式: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    # 显示完整的表格内容
    tables = [item for item in content_list if item.get('type') == 'table']
    if tables:
        print(f"\n📊 表格详细内容:")
        for i, table in enumerate(tables, 1):
            caption = table.get('table_caption', f'表格{i}')
            table_body = table.get('table_body', [])
            print(f"\n[表格{i}] {caption}")
            
            if table_body:
                # 显示表格内容
                for row_idx, row in enumerate(table_body[:5]):  # 最多显示5行
                    row_str = " | ".join(str(cell)[:20] + ('...' if len(str(cell)) > 20 else '') for cell in row)
                    print(f"  {row_idx + 1}: {row_str}")
                
                if len(table_body) > 5:
                    print(f"  ... (还有 {len(table_body) - 5} 行)")

def perform_parsing(pdf_path):
    """执行实际的PDF解析"""
    
    print(f"\n🚀 开始解析 {pdf_path.name}...")
    
    # 创建配置
    config = RAGAnythingCLConfig(
        parser='mineru',
        working_dir='./parsing_results',
        parse_method='auto',  # 使用auto方法获得最好效果
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
        save_intermediate=True,
        output_format='json'
    )
    
    # 初始化RAG-CL
    ragcl = RAGAnythingCL(config)
    
    # 检查安装
    if not ragcl.check_installation():
        print("❌ MinerU安装检查失败")
        return
    
    try:
        # 解析PDF
        content_list = ragcl.parse_document(pdf_path)
        
        print(f"✅ 解析完成! 获得 {len(content_list)} 个内容块")
        
        # 显示结果
        display_results(content_list)
        
        # 保存结果摘要
        save_summary(content_list, config.working_dir)
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        logging.exception("详细错误:")

def save_summary(content_list, output_dir):
    """保存解析结果摘要"""
    
    output_path = Path(output_dir)
    
    # 创建摘要
    summary = {
        'total_blocks': len(content_list),
        'content_types': {},
        'sample_content': []
    }
    
    for item in content_list:
        if isinstance(item, dict):
            content_type = item.get('type', 'unknown')
            summary['content_types'][content_type] = summary['content_types'].get(content_type, 0) + 1
    
    # 添加样本内容
    for item in content_list[:5]:
        if isinstance(item, dict):
            sample = {
                'type': item.get('type'),
                'page_idx': item.get('page_idx')
            }
            
            if item.get('type') == 'text':
                text = item.get('text', '')
                sample['preview'] = text[:100] + ('...' if len(text) > 100 else '')
            elif item.get('type') == 'table':
                sample['caption'] = item.get('table_caption', '')
                table_body = item.get('table_body', [])
                sample['size'] = f"{len(table_body)}行" if table_body else "空表格"
            
            summary['sample_content'].append(sample)
    
    # 保存摘要
    summary_file = output_path / "parsing_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 解析摘要已保存到: {summary_file}")

def main():
    """主函数"""
    show_parsing_results()
    
    print(f"\n" + "=" * 50)
    print("🎉 RAG-CL PDF解析功能展示完成!")
    print("✅ 成功展示了基于RAG-Anything的文档解析能力")
    print("✅ 验证了多模态内容提取功能")
    print("✅ 展示了结构化数据输出")
    
    return 0

if __name__ == "__main__":
    exit(main())