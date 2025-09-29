#!/usr/bin/env python3
"""
完全按照RAG-Anything方式实现的实体提取器

直接提取RAG-Anything中的实体提取逻辑，确保效果一致
"""

import re
import json
import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import logging

# OpenAI API客户端
from openai import OpenAI

logger = logging.getLogger(__name__)


class RAGAnythingEntityExtractor:
    """
    完全按照RAG-Anything方式实现的实体提取器
    
    直接使用RAG-Anything中的prompts和处理逻辑
    """
    
    def __init__(
        self,
        api_base: str = "https://api.chatanywhere.tech/v1",
        api_key: str = "sk-FiF5mSQ5EF1QrvI4FrVB7ZnrmXCjlJDUokJfTJ7HuNP5KQ78",
        model: str = "gpt-4o-mini"
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
        
        # 使用RAG-Anything的提示模板
        self.prompts = self._init_raganything_prompts()
    
    def _init_raganything_prompts(self) -> Dict[str, str]:
        """初始化RAG-Anything风格的提示模板"""
        return {
            # 直接采用RAG-Anything modalprocessors中的提示逻辑
            "vision_prompt": """Please analyze this image in detail and provide a JSON response with the following structure:

{{
    "detailed_description": "A comprehensive and detailed visual description of the image following these guidelines:
    - Describe the overall composition and layout
    - Identify all objects, people, text, and visual elements
    - Explain relationships between elements
    - Note colors, lighting, and visual style
    - Describe any actions or activities shown
    - Include technical details if relevant (charts, diagrams, etc.)
    - Always use specific names instead of pronouns",
    "entity_info": {{
        "entity_name": "{entity_name}",
        "entity_type": "image",
        "summary": "concise summary of the image content and its significance (max 100 words)"
    }}
}}

Additional context:
- Image Path: {image_path}
- Captions: {captions}
- Footnotes: {footnotes}

Focus on providing accurate, detailed visual analysis that would be useful for knowledge retrieval.""",

            "table_prompt": """Please analyze this table content and provide a JSON response with the following structure:

{{
    "detailed_description": "A comprehensive analysis of the table including:
    - Table structure and organization
    - Column headers and their meanings
    - Key data points and patterns
    - Statistical insights and trends
    - Relationships between data elements
    - Significance of the data presented
    Always use specific names and values instead of general references.",
    "entity_info": {{
        "entity_name": "{entity_name}",
        "entity_type": "table",
        "summary": "concise summary of the table's purpose and key findings (max 100 words)"
    }}
}}

Table Information:
Image Path: {table_img_path}
Caption: {table_caption}
Body: {table_body}
Footnotes: {table_footnote}

Focus on extracting meaningful insights and relationships from the tabular data.""",

            "generic_text_extraction": """Extract entities and relationships from the following text content:

Text: {content}

Please provide a JSON response with:
{{
    "entities": [
        {{
            "name": "entity name",
            "type": "entity type (Person, Organization, Location, Concept, Product, etc.)",
            "description": "brief description",
            "relevance_score": 0.0-1.0
        }}
    ],
    "relationships": [
        {{
            "from": "source entity",
            "to": "target entity",
            "relation": "relationship type",
            "description": "relationship description",
            "confidence": 0.0-1.0
        }}
    ],
    "summary": "brief summary of the content"
}}

Focus on identifying:
- Key entities (names, concepts, technical terms)
- Semantic relationships between entities
- Important factual information"""
        }
    
    async def extract_entities_from_content_list(
        self,
        content_list: List[Dict[str, Any]],
        extract_relations: bool = True
    ) -> Dict[str, Any]:
        """
        从内容列表中提取实体和关系
        
        使用RAG-Anything的处理逻辑
        """
        logger.info(f"开始使用RAG-Anything方式提取实体，处理{len(content_list)}个内容块")
        
        all_entities = []
        all_relationships = []
        
        # 按内容类型分别处理
        for i, item in enumerate(content_list):
            if not isinstance(item, dict):
                continue
            
            content_type = item.get('type', 'text')
            
            try:
                if content_type == 'text':
                    result = await self._process_text_content(item, i)
                elif content_type == 'table':
                    result = await self._process_table_content(item, i)
                elif content_type == 'image':
                    result = await self._process_image_content(item, i)
                else:
                    result = await self._process_generic_content(item, i)
                
                if result:
                    entities = result.get('entities', [])
                    relationships = result.get('relationships', [])
                    
                    # 添加来源信息
                    for entity in entities:
                        entity['source_block'] = i
                        entity['source_page'] = item.get('page_idx', 0)
                        entity['source_type'] = content_type
                    
                    for rel in relationships:
                        rel['source_block'] = i
                        rel['source_page'] = item.get('page_idx', 0)
                    
                    all_entities.extend(entities)
                    all_relationships.extend(relationships)
                
                # 控制请求频率
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"处理内容块{i}失败: {str(e)}")
                continue
        
        # 分析文档结构
        doc_analysis = await self._analyze_document_structure(content_list)
        
        result = {
            'entities': all_entities,
            'relationships': all_relationships,
            'document_analysis': doc_analysis,
            'statistics': {
                'total_entities': len(all_entities),
                'total_relationships': len(all_relationships),
                'content_blocks_processed': len(content_list),
                'processing_method': 'raganything_style'
            }
        }
        
        logger.info(f"RAG-Anything风格实体提取完成: {len(all_entities)}个实体, {len(all_relationships)}个关系")
        return result
    
    async def _process_text_content(self, item: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """处理文本内容"""
        text = item.get('text', '').strip()
        if len(text) < 10:
            return None
        
        prompt = self.prompts['generic_text_extraction'].format(content=text[:2000])
        
        response = await self._call_llm(prompt)
        return self._parse_json_response(response)
    
    async def _process_table_content(self, item: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """处理表格内容"""
        table_caption = item.get('table_caption', '未命名表格')
        table_body = item.get('table_body', [])
        
        if not table_body:
            return None
        
        # 格式化表格数据
        table_str = self._format_table_data(table_body)
        
        # 构建实体名称
        entity_name = f"Table_{index}_{table_caption[:20]}"
        
        prompt = self.prompts['table_prompt'].format(
            entity_name=entity_name,
            table_img_path=item.get('img_path', ''),
            table_caption=table_caption,
            table_body=table_str,
            table_footnote=item.get('table_footnote', '')
        )
        
        response = await self._call_llm(prompt)
        result = self._parse_json_response(response)
        
        if result and 'entity_info' in result:
            # 将模态实体转换为标准实体格式
            entity_info = result['entity_info']
            entity = {
                "name": entity_info.get('entity_name', entity_name),
                "type": entity_info.get('entity_type', 'table'),
                "description": result.get('detailed_description', ''),
                "summary": entity_info.get('summary', ''),
                "relevance_score": 1.0
            }
            
            return {
                "entities": [entity],
                "relationships": [],
                "content_analysis": result
            }
        
        return result
    
    async def _process_image_content(self, item: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """处理图片内容"""
        image_caption = item.get('image_caption', '未命名图片')
        
        # 构建实体名称
        entity_name = f"Image_{index}_{image_caption[:20]}"
        
        prompt = self.prompts['vision_prompt'].format(
            entity_name=entity_name,
            image_path=item.get('img_path', ''),
            captions=image_caption,
            footnotes=item.get('footnotes', '')
        )
        
        response = await self._call_llm(prompt)
        result = self._parse_json_response(response)
        
        if result and 'entity_info' in result:
            # 将模态实体转换为标准实体格式
            entity_info = result['entity_info']
            entity = {
                "name": entity_info.get('entity_name', entity_name),
                "type": entity_info.get('entity_type', 'image'),
                "description": result.get('detailed_description', ''),
                "summary": entity_info.get('summary', ''),
                "relevance_score": 1.0
            }
            
            return {
                "entities": [entity],
                "relationships": [],
                "content_analysis": result
            }
        
        return result
    
    async def _process_generic_content(self, item: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """处理通用内容"""
        content = str(item.get('text', item.get('content', '')))[:1000]
        if len(content) < 5:
            return None
        
        prompt = self.prompts['generic_text_extraction'].format(content=content)
        
        response = await self._call_llm(prompt)
        return self._parse_json_response(response)
    
    def _format_table_data(self, table_body: List[List]) -> str:
        """格式化表格数据"""
        if not table_body:
            return "空表格"
        
        formatted_rows = []
        for i, row in enumerate(table_body[:10]):  # 限制行数
            row_str = " | ".join(str(cell)[:50] for cell in row[:8])  # 限制列数和单元格长度
            formatted_rows.append(f"行{i+1}: {row_str}")
        
        return "\n".join(formatted_rows)
    
    async def _analyze_document_structure(self, content_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析文档结构"""
        content_types = {}
        pages = set()
        
        for item in content_list:
            if isinstance(item, dict):
                content_type = item.get('type', 'unknown')
                content_types[content_type] = content_types.get(content_type, 0) + 1
                
                page_idx = item.get('page_idx')
                if page_idx is not None:
                    pages.add(page_idx)
        
        return {
            "document_info": {
                "title": "Processed Document",
                "type": "Technical Document",
                "domain": "General",
                "language": "Mixed"
            },
            "content_statistics": {
                "total_pages": len(pages),
                "content_types": content_types
            },
            "structure_entities": [],
            "global_entities": []
        }
    
    async def _call_llm(self, prompt: str) -> Optional[str]:
        """调用LLM"""
        try:
            if not self.client:
                logger.error("OpenAI客户端未初始化")
                return None
            
            def sync_call():
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert entity extraction and analysis specialist. Always return valid JSON format responses."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.1
                )
                return response.choices[0].message.content
            
            # 在线程池中执行同步调用
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, sync_call)
            return result
            
        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
            return None
    
    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """解析JSON响应"""
        if not response:
            return None
        
        # 尝试多种方法解析JSON
        json_candidates = []
        
        # 方法1: 直接解析
        json_candidates.append(response.strip())
        
        # 方法2: 提取代码块中的JSON
        code_block_pattern = r'```(?:json)?\\s*([\\s\\S]*?)```'
        matches = re.findall(code_block_pattern, response, re.IGNORECASE)
        json_candidates.extend(matches)
        
        # 方法3: 提取大括号内容
        brace_pattern = r'\\{[\\s\\S]*\\}'
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


# 兼容性适配器
class EntityExtractor:
    """实体提取器适配器，使用RAG-Anything方式"""
    
    def __init__(
        self,
        api_base: str = "https://api.chatanywhere.tech/v1",
        api_key: str = "sk-FiF5mSQ5EF1QrvI4FrVB7ZnrmXCjlJDUokJfTJ7HuNP5KQ78",
        model: str = "gpt-4o-mini"
    ):
        self.extractor = RAGAnythingEntityExtractor(api_base, api_key, model)
    
    async def extract_entities_from_content_list(
        self,
        content_list: List[Dict[str, Any]],
        extract_relations: bool = True
    ) -> Dict[str, Any]:
        return await self.extractor.extract_entities_from_content_list(content_list, extract_relations)
    
    def extract_entities_sync(
        self,
        content_list: List[Dict[str, Any]],
        extract_relations: bool = True
    ) -> Dict[str, Any]:
        return self.extractor.extract_entities_sync(content_list)