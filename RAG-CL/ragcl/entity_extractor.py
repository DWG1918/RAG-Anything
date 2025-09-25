"""
实体提取模块

基于RAG-Anything的实体提取功能，适配RAG-CL项目使用
支持从解析的文档内容中提取实体和关系
"""

import re
import json
import asyncio
from typing import Dict, Any, List, Optional
import logging

# LLM API 客户端
from openai import OpenAI

logger = logging.getLogger(__name__)


class EntityExtractor:
    """
    实体提取器
    
    从文档解析结果中提取实体、关系和结构化信息
    """
    
    def __init__(
        self,
        api_base: str = "https://api.chatanywhere.tech/v1",
        api_key: str = "sk-FiF5mSQ5EF1QrvI4FrVB7ZnrmXCjlJDUokJfTJ7HuNP5KQ78",
        model: str = "gpt-3.5-turbo"
    ):
        """
        初始化实体提取器
        
        Args:
            api_base: LLM API 基础URL
            api_key: API 密钥
            model: 使用的模型名称
        """
        self.api_base = api_base
        self.api_key = api_key
        self.model = model
        
        # 配置OpenAI客户端
        self.client = None
        if api_key:
            self.client = OpenAI(
                api_key=api_key,
                base_url=api_base
            )
        
        # 提示模板
        self.prompts = self._init_prompts()
    
    def _init_prompts(self) -> Dict[str, str]:
        """初始化提示模板"""
        return {
            "text_entity_extraction": """请分析以下文本内容并提取实体信息，返回JSON格式结果：

文本内容：
{content}

请提取并返回以下格式的JSON：
{{
    "entities": [
        {{
            "name": "实体名称",
            "type": "实体类型",
            "description": "实体描述",
            "relevance_score": 评分(0-1)
        }}
    ],
    "summary": "内容摘要",
    "key_concepts": ["关键概念1", "关键概念2"],
    "context": "上下文信息"
}}

重点关注：
- 专业术语和技术名词
- 人名、地名、组织名
- 产品名称、型号、规格
- 数值、日期、标准
- 重要概念和定义""",
            
            "table_entity_extraction": """请分析以下表格内容并提取结构化信息：

表格标题：{caption}
表格内容：
{table_data}

请返回JSON格式结果：
{{
    "table_summary": "表格内容摘要",
    "key_data": {{
        "headers": ["表头1", "表头2"],
        "key_values": [
            {{"header": "表头", "values": ["值1", "值2"], "significance": "重要性描述"}}
        ]
    }},
    "extracted_entities": [
        {{
            "name": "实体名称",
            "type": "data_point/parameter/standard",
            "value": "数值",
            "description": "描述"
        }}
    ],
    "relationships": [
        {{"from": "实体1", "to": "实体2", "relation": "关系类型", "description": "关系描述"}}
    ]
}}""",
            
            "document_structure_analysis": """请分析以下文档结构并提取文档级别的实体：

文档内容块：
{content_blocks}

请返回JSON格式结果：
{{
    "document_info": {{
        "title": "文档标题",
        "type": "文档类型",
        "domain": "领域",
        "language": "语言"
    }},
    "structure_entities": [
        {{
            "name": "章节/部分名称",
            "type": "section/chapter/appendix",
            "content_summary": "内容摘要",
            "page_range": [开始页, 结束页]
        }}
    ],
    "global_entities": [
        {{
            "name": "全局实体名称",
            "type": "实体类型",
            "frequency": 出现频次,
            "importance": "重要性评分",
            "description": "描述"
        }}
    ]
}}"""
        }
    
    async def extract_entities_from_content_list(
        self,
        content_list: List[Dict[str, Any]],
        extract_relations: bool = True
    ) -> Dict[str, Any]:
        """
        从内容块列表中提取实体
        
        Args:
            content_list: 文档解析后的内容块列表
            extract_relations: 是否提取实体关系
            
        Returns:
            Dict: 提取的实体和关系信息
        """
        logger.info(f"开始从{len(content_list)}个内容块中提取实体...")
        
        all_entities = []
        all_relationships = []
        text_blocks = []
        table_blocks = []
        
        # 分类内容块
        for i, block in enumerate(content_list):
            if not isinstance(block, dict):
                continue
            
            content_type = block.get('type', 'unknown')
            block['block_index'] = i  # 添加块索引
            
            if content_type == 'text':
                text_blocks.append(block)
            elif content_type == 'table':
                table_blocks.append(block)
        
        logger.info(f"识别到 {len(text_blocks)} 个文本块, {len(table_blocks)} 个表格块")
        
        # 处理文本块
        if text_blocks:
            text_entities = await self._extract_text_entities(text_blocks)
            all_entities.extend(text_entities.get('entities', []))
        
        # 处理表格块
        if table_blocks:
            table_entities = await self._extract_table_entities(table_blocks)
            all_entities.extend(table_entities.get('entities', []))
        
        # 文档结构分析
        doc_analysis = await self._analyze_document_structure(content_list)
        
        # 提取关系（如果需要）
        if extract_relations and len(all_entities) > 1:
            relationships = await self._extract_entity_relationships(all_entities)
            all_relationships.extend(relationships)
        
        return {
            'entities': all_entities,
            'relationships': all_relationships,
            'document_analysis': doc_analysis,
            'statistics': {
                'total_entities': len(all_entities),
                'total_relationships': len(all_relationships),
                'text_blocks_processed': len(text_blocks),
                'table_blocks_processed': len(table_blocks)
            }
        }
    
    async def _extract_text_entities(self, text_blocks: List[Dict]) -> Dict[str, Any]:
        """从文本块中提取实体"""
        logger.info(f"处理 {len(text_blocks)} 个文本块...")
        
        all_entities = []
        
        # 合并相邻的短文本块以提高效率
        processed_blocks = self._merge_text_blocks(text_blocks)
        
        for block in processed_blocks:
            text_content = block.get('text', '').strip()
            if len(text_content) < 10:  # 跳过太短的文本
                continue
            
            try:
                # 使用LLM提取实体
                entities_result = await self._call_llm_for_extraction(
                    self.prompts['text_entity_extraction'].format(content=text_content)
                )
                
                if entities_result and 'entities' in entities_result:
                    # 为每个实体添加源信息
                    for entity in entities_result['entities']:
                        entity['source_block'] = block.get('block_index', -1)
                        entity['source_page'] = block.get('page_idx', 0)
                        entity['source_type'] = 'text'
                    
                    all_entities.extend(entities_result['entities'])
                
                # 防止API调用过于频繁
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"处理文本块时出错: {str(e)}")
                continue
        
        return {'entities': all_entities}
    
    async def _extract_table_entities(self, table_blocks: List[Dict]) -> Dict[str, Any]:
        """从表格块中提取实体"""
        logger.info(f"处理 {len(table_blocks)} 个表格块...")
        
        all_entities = []
        
        for block in table_blocks:
            table_caption = block.get('table_caption', '未命名表格')
            table_body = block.get('table_body', [])
            
            if not table_body:
                continue
            
            try:
                # 格式化表格数据
                table_data = self._format_table_for_llm(table_body)
                
                # 使用LLM分析表格
                table_result = await self._call_llm_for_extraction(
                    self.prompts['table_entity_extraction'].format(
                        caption=table_caption,
                        table_data=table_data
                    )
                )
                
                if table_result and 'extracted_entities' in table_result:
                    # 为表格实体添加源信息
                    for entity in table_result['extracted_entities']:
                        entity['source_block'] = block.get('block_index', -1)
                        entity['source_page'] = block.get('page_idx', 0)
                        entity['source_type'] = 'table'
                        entity['source_caption'] = table_caption
                    
                    all_entities.extend(table_result['extracted_entities'])
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"处理表格块时出错: {str(e)}")
                continue
        
        return {'entities': all_entities}
    
    async def _analyze_document_structure(self, content_list: List[Dict]) -> Dict[str, Any]:
        """分析文档结构"""
        logger.info("分析文档整体结构...")
        
        # 提取结构信息
        structure_info = []
        for block in content_list[:10]:  # 只分析前10个块以识别结构
            if isinstance(block, dict):
                structure_info.append({
                    'type': block.get('type', 'unknown'),
                    'text_preview': str(block.get('text', block.get('table_caption', '')))[:100],
                    'page': block.get('page_idx', 0)
                })
        
        try:
            doc_analysis = await self._call_llm_for_extraction(
                self.prompts['document_structure_analysis'].format(
                    content_blocks=json.dumps(structure_info, ensure_ascii=False, indent=2)
                )
            )
            return doc_analysis or {}
        except Exception as e:
            logger.error(f"文档结构分析失败: {str(e)}")
            return {}
    
    async def _extract_entity_relationships(self, entities: List[Dict]) -> List[Dict]:
        """提取实体间关系"""
        if len(entities) < 2:
            return []
        
        logger.info(f"分析 {len(entities)} 个实体的关系...")
        
        # 构建实体关系提取提示
        entity_names = [entity.get('name', '') for entity in entities[:20]]  # 限制数量避免token过多
        
        relationship_prompt = f"""基于以下实体列表，请分析它们之间可能的关系：

实体列表：
{json.dumps(entity_names, ensure_ascii=False, indent=2)}

请返回JSON格式的关系：
{{
    "relationships": [
        {{
            "from": "实体1",
            "to": "实体2", 
            "relation": "关系类型",
            "description": "关系描述",
            "confidence": 置信度(0-1)
        }}
    ]
}}

关系类型包括：part_of, related_to, depends_on, defines, measures, etc."""
        
        try:
            relationships_result = await self._call_llm_for_extraction(relationship_prompt)
            return relationships_result.get('relationships', []) if relationships_result else []
        except Exception as e:
            logger.error(f"关系提取失败: {str(e)}")
            return []
    
    def _merge_text_blocks(self, text_blocks: List[Dict]) -> List[Dict]:
        """合并相邻的短文本块以提高处理效率"""
        if not text_blocks:
            return []
        
        merged_blocks = []
        current_block = None
        
        for block in text_blocks:
            text = block.get('text', '').strip()
            
            # 如果文本很短且当前有累积块，则合并
            if len(text) < 200 and current_block is not None:
                current_block['text'] += f"\n{text}"
                current_block['merged_blocks'] = current_block.get('merged_blocks', []) + [block.get('block_index', -1)]
            else:
                # 保存之前的块（如果有）
                if current_block is not None:
                    merged_blocks.append(current_block)
                
                # 开始新的块
                current_block = block.copy()
        
        # 添加最后一个块
        if current_block is not None:
            merged_blocks.append(current_block)
        
        return merged_blocks
    
    def _format_table_for_llm(self, table_body: List[List]) -> str:
        """格式化表格数据供LLM处理"""
        if not table_body:
            return "空表格"
        
        # 转换为文本格式
        formatted_rows = []
        for i, row in enumerate(table_body[:10]):  # 限制行数
            row_str = " | ".join(str(cell)[:50] for cell in row[:10])  # 限制列数和单元格长度
            formatted_rows.append(f"行{i+1}: {row_str}")
        
        return "\n".join(formatted_rows)
    
    async def _call_llm_for_extraction(self, prompt: str) -> Optional[Dict[str, Any]]:
        """调用LLM进行信息提取"""
        try:
            # 使用OpenAI API
            response = await self._async_openai_call(prompt)
            
            if response:
                # 尝试解析JSON响应
                return self._parse_llm_response(response)
            
        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
        
        return None
    
    async def _async_openai_call(self, prompt: str) -> Optional[str]:
        """异步调用OpenAI API"""
        try:
            if not self.client:
                logger.error("OpenAI客户端未初始化")
                return None
            
            # 使用新的OpenAI API格式
            def sync_call():
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的实体提取和分析专家，请严格按照JSON格式要求返回结果。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.1
                )
                return response.choices[0].message.content
            
            # 在线程池中执行同步调用
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, sync_call)
            return result
            
        except Exception as e:
            logger.error(f"OpenAI API调用错误: {str(e)}")
            return None
    
    def _parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
        """解析LLM返回的JSON响应"""
        if not response:
            return None
        
        # 尝试多种方法解析JSON
        json_candidates = []
        
        # 方法1: 直接解析
        json_candidates.append(response.strip())
        
        # 方法2: 提取代码块中的JSON
        code_block_pattern = r'```(?:json)?\s*([\s\S]*?)```'
        matches = re.findall(code_block_pattern, response, re.IGNORECASE)
        json_candidates.extend(matches)
        
        # 方法3: 提取大括号内容
        brace_pattern = r'\{[\s\S]*\}'
        matches = re.findall(brace_pattern, response)
        json_candidates.extend(matches)
        
        # 尝试解析每个候选
        for candidate in json_candidates:
            try:
                candidate = candidate.strip()
                if candidate:
                    parsed = json.loads(candidate)
                    return parsed
            except json.JSONDecodeError:
                continue
        
        logger.warning("无法解析LLM响应为JSON格式")
        return None
    
    def extract_entities_sync(self, content_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """同步版本的实体提取接口"""
        try:
            # 创建新的事件循环或使用现有的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.extract_entities_from_content_list(content_list)
                )
                return result
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"同步实体提取失败: {str(e)}")
            return {
                'entities': [],
                'relationships': [],
                'document_analysis': {},
                'statistics': {'error': str(e)}
            }