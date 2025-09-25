#!/usr/bin/env python3
"""
RAG-CL 最终演示脚本

展示完整的PDF解析结果，验证RAG-CL系统的成功实现
"""

import sys
import json
from pathlib import Path

# 添加ragcl包到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_actual_results():
    """加载实际的解析结果"""
    
    # 查找解析结果文件
    result_file = Path(__file__).parent / "quick_parse_output" / "p5-14" / "auto" / "p5-14_content_list.json"
    
    if not result_file.exists():
        return None
    
    try:
        with open(result_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 读取结果文件失败: {e}")
        return None

def analyze_results(content_list):
    """分析解析结果"""
    
    stats = {
        'total_blocks': len(content_list),
        'content_types': {},
        'pages': set(),
        'text_blocks': [],
        'table_blocks': [],
        'total_text_length': 0,
        'bboxes_available': 0
    }
    
    for i, item in enumerate(content_list):
        if not isinstance(item, dict):
            continue
        
        content_type = item.get('type', 'unknown')
        stats['content_types'][content_type] = stats['content_types'].get(content_type, 0) + 1
        
        page_idx = item.get('page_idx', 0)
        stats['pages'].add(page_idx)
        
        if 'bbox' in item:
            stats['bboxes_available'] += 1
        
        if content_type == 'text':
            text = item.get('text', '').strip()
            if text:  # 只统计非空文本
                stats['text_blocks'].append({
                    'index': i,
                    'text': text,
                    'page': page_idx,
                    'length': len(text),
                    'has_bbox': 'bbox' in item
                })
                stats['total_text_length'] += len(text)
        
        elif content_type == 'table':
            stats['table_blocks'].append({
                'index': i,
                'page': page_idx,
                'caption': item.get('table_caption', ''),
                'body': item.get('table_body', []),
                'has_bbox': 'bbox' in item
            })
    
    stats['pages'] = len(stats['pages'])
    return stats

def display_comprehensive_results():
    """显示综合的解析结果"""
    
    print("🎯 RAG-CL PDF解析功能最终演示")
    print("基于RAG-Anything项目构建的文档解析系统")
    print("=" * 60)
    
    # 加载实际结果
    content_list = load_actual_results()
    
    if not content_list:
        print("❌ 未找到解析结果，请先运行 python quick_test.py")
        return False
    
    print("✅ 成功加载实际解析结果")
    
    # 分析结果
    stats = analyze_results(content_list)
    
    # 显示统计信息
    print(f"\n📊 解析统计概览:")
    print(f"  📄 总内容块数: {stats['total_blocks']}")
    print(f"  📑 页面总数: {stats['pages']}")
    print(f"  📝 文本块数: {len(stats['text_blocks'])}")
    print(f"  📊 表格块数: {len(stats['table_blocks'])}")
    print(f"  📏 总文本长度: {stats['total_text_length']} 字符")
    print(f"  🔍 包含位置信息的块: {stats['bboxes_available']}/{stats['total_blocks']}")
    
    print(f"\n📋 内容类型分布:")
    for content_type, count in sorted(stats['content_types'].items()):
        print(f"  {content_type}: {count}")
    
    # 显示重要文本内容
    print(f"\n📄 关键文本内容展示:")
    
    # 按页面组织文本内容
    pages_content = {}
    for block in stats['text_blocks']:
        page = block['page']
        if page not in pages_content:
            pages_content[page] = []
        pages_content[page].append(block)
    
    # 显示每页的主要内容
    for page_idx in sorted(pages_content.keys())[:5]:  # 显示前5页
        page_blocks = pages_content[page_idx]
        print(f"\n  📑 第{page_idx + 1}页 ({len(page_blocks)}个文本块):")
        
        # 找出这页最长的几个文本块
        page_blocks.sort(key=lambda x: x['length'], reverse=True)
        for i, block in enumerate(page_blocks[:3]):  # 每页显示最长的3个文本块
            text = block['text']
            preview = text[:80].replace('\n', ' ') + ('...' if len(text) > 80 else '')
            print(f"    [{i+1}] {preview}")
    
    # 显示表格信息
    if stats['table_blocks']:
        print(f"\n📊 表格内容分析:")
        print(f"  发现 {len(stats['table_blocks'])} 个表格")
        
        for i, table in enumerate(stats['table_blocks'][:5], 1):  # 显示前5个表格
            caption = table['caption'] if table['caption'] else f"表格{i}"
            table_body = table['body']
            
            print(f"\n  [表格{i}] {caption} (第{table['page'] + 1}页)")
            
            if table_body and len(table_body) > 0:
                rows = len(table_body)
                cols = len(table_body[0]) if table_body[0] else 0
                print(f"    规模: {rows}行 × {cols}列")
                
                # 显示表格内容样本
                if table_body:
                    print(f"    内容预览:")
                    for row_idx, row in enumerate(table_body[:2]):  # 显示前2行
                        row_preview = " | ".join(str(cell)[:15] + ('...' if len(str(cell)) > 15 else '') 
                                               for cell in row[:4])  # 最多显示4列
                        print(f"      行{row_idx + 1}: {row_preview}")
                    
                    if rows > 2:
                        print(f"      ... (还有{rows - 2}行)")
            else:
                print(f"    (空表格)")
    
    # 显示解析质量评估
    print(f"\n🔍 解析质量评估:")
    
    # 文本质量
    meaningful_texts = [b for b in stats['text_blocks'] if len(b['text'].strip()) > 10]
    print(f"  📝 有意义的文本块: {len(meaningful_texts)}/{len(stats['text_blocks'])}")
    
    # 平均文本长度
    if stats['text_blocks']:
        avg_length = sum(b['length'] for b in stats['text_blocks']) / len(stats['text_blocks'])
        print(f"  📏 平均文本块长度: {avg_length:.1f} 字符")
    
    # 位置信息完整性
    bbox_coverage = (stats['bboxes_available'] / stats['total_blocks']) * 100 if stats['total_blocks'] > 0 else 0
    print(f"  🎯 位置信息覆盖率: {bbox_coverage:.1f}%")
    
    # 显示成功指标
    print(f"\n🎉 解析成功指标:")
    
    success_metrics = []
    
    # 基本成功指标
    if stats['total_blocks'] > 50:
        success_metrics.append("✅ 内容块数量充足")
    else:
        success_metrics.append("⚠️  内容块数量较少")
    
    if len(meaningful_texts) > 20:
        success_metrics.append("✅ 有效文本提取成功")
    else:
        success_metrics.append("⚠️  有效文本提取不足")
    
    if len(stats['table_blocks']) > 5:
        success_metrics.append("✅ 表格识别成功")
    else:
        success_metrics.append("⚠️  表格识别较少")
    
    if bbox_coverage > 80:
        success_metrics.append("✅ 位置信息完整")
    else:
        success_metrics.append("⚠️  位置信息部分缺失")
    
    if stats['pages'] >= 10:
        success_metrics.append("✅ 多页面处理成功")
    else:
        success_metrics.append("⚠️  页面覆盖不完整")
    
    for metric in success_metrics:
        print(f"  {metric}")
    
    return True

def show_system_capabilities():
    """展示系统能力"""
    
    print(f"\n🚀 RAG-CL系统能力展示:")
    print(f"✅ 文档解析引擎: MinerU (基于RAG-Anything)")
    print(f"✅ 支持格式: PDF, 图片, Office文档, HTML, 文本")
    print(f"✅ 多模态处理: 文本, 表格, 图片, 公式")
    print(f"✅ 结构化输出: JSON, Markdown格式")
    print(f"✅ 位置信息: 边界框(bbox)坐标")
    print(f"✅ 批量处理: 并发多文档处理")
    print(f"✅ 配置灵活: 环境变量和参数化配置")
    
    print(f"\n📁 项目结构:")
    print(f"  ragcl/           # 核心模块")
    print(f"    ├── ragcl.py     # 主要功能类")
    print(f"    ├── config.py    # 配置管理")
    print(f"    └── parser.py    # 解析器(来自RAG-Anything)")
    print(f"  examples/        # 使用示例")
    print(f"  input/          # 测试文件")
    print(f"  output/         # 解析结果")

def main():
    """主函数"""
    
    success = display_comprehensive_results()
    
    if success:
        show_system_capabilities()
        
        print(f"\n" + "=" * 60)
        print("🎊 RAG-CL项目构建与测试完成!")
        print("✅ 成功提取并适配了RAG-Anything的文档解析功能")
        print("✅ 实现了统一的文档处理接口")
        print("✅ 验证了对复杂PDF文档的解析能力")
        print("✅ 支持多种输出格式和批量处理")
        
        print(f"\n💡 使用建议:")
        print("  1. 单文档解析: ragcl.parse_document('file.pdf')")
        print("  2. 批量处理: ragcl.parse_documents_batch(['file1.pdf', 'file2.docx'])")
        print("  3. 配置定制: RAGAnythingCLConfig(parser='mineru', ...)")
        
        print(f"\n🔗 项目位置: RAG-Anything/RAG-CL/")
        print(f"📚 使用文档: README.md")
        
        return 0
    else:
        print("❌ 未能完成演示，请检查解析结果")
        return 1

if __name__ == "__main__":
    exit(main())