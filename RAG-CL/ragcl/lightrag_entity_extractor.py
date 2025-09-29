#!/usr/bin/env python3
"""
基于LightRAG的实体提取器

完全按照RAG-Anything的方式实现实体提取，确保与RAG-Anything效果一致
"""

import asyncio
import logging
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

# LightRAG相关导入
from lightrag.utils import compute_mdhash_id
from lightrag.operate import extract_entities 
from lightrag.kg.shared_storage import get_namespace_data, get_pipeline_status_lock
from lightrag import LightRAG

logger = logging.getLogger(__name__)


@dataclass
class LightRAGConfig:
    """LightRAG配置"""
    working_dir: str = "./lightrag_workspace"
    llm_model: str = "gpt-4o-mini"
    llm_api_base: str = "https://api.chatanywhere.tech/v1" 
    llm_api_key: str = "sk-FiF5mSQ5EF1QrvI4FrVB7ZnrmXCjlJDUokJfTJ7HuNP5KQ78"
    embedding_model: str = "text-embedding-ada-002"
    embedding_api_base: str = "https://api.chatanywhere.tech/v1"
    embedding_api_key: str = "sk-FiF5mSQ5EF1QrvI4FrVB7ZnrmXCjlJDUokJfTJ7HuNP5KQ78"


class LightRAGEntityExtractor:
    """
    基于LightRAG的实体提取器
    
    完全采用RAG-Anything中使用的LightRAG方法进行实体提取
    """
    
    def __init__(self, config: LightRAGConfig = None):
        """
        初始化实体提取器
        
        Args:
            config: LightRAG配置
        """
        self.config = config or LightRAGConfig()
        self.lightrag = None
        self._init_lightrag()
    
    def _init_lightrag(self):
        """初始化LightRAG实例"""
        try:
            # 创建LightRAG实例，配置与RAG-Anything一致
            self.lightrag = LightRAG(
                working_dir=self.config.working_dir,
                llm_model_func=self._create_llm_model_func(),
                embedding_func=self._create_embedding_func(),
            )
            logger.info("LightRAG initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LightRAG: {e}")
            raise
    
    def _create_llm_model_func(self):
        """创建LLM模型函数"""
        try:
            from lightrag.llm import openai_complete_if_cache
            
            async def llm_model_func(
                prompt,
                system_prompt=None,
                history_messages=None,
                **kwargs
            ):
                return await openai_complete_if_cache(
                    model=self.config.llm_model,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    history_messages=history_messages,
                    api_key=self.config.llm_api_key,
                    base_url=self.config.llm_api_base,
                    **kwargs
                )
            
            return llm_model_func
        except ImportError:
            logger.warning("Could not import LightRAG LLM functions")
            return None
    
    def _create_embedding_func(self):
        """创建嵌入函数"""
        try:
            # 使用更稳定的导入方式
            from lightrag.llm import openai_embedding
            
            async def embedding_func(texts: List[str]) -> List[List[float]]:
                return await openai_embedding(
                    texts,
                    model=self.config.embedding_model,
                    api_key=self.config.embedding_api_key,
                    base_url=self.config.embedding_api_base
                )
            
            return embedding_func
        except ImportError:
            logger.warning("Could not import LightRAG embedding functions, using fallback")
            return None
    
    async def extract_entities_from_content_list(
        self,
        content_list: List[Dict[str, Any]],
        extract_relations: bool = True
    ) -> Dict[str, Any]:
        """
        从内容列表中提取实体和关系
        
        Args:
            content_list: 解析后的内容列表
            extract_relations: 是否提取关系
            
        Returns:
            提取的实体和关系
        """
        logger.info(f"开始使用LightRAG提取实体，处理{len(content_list)}个内容块")
        
        try:
            # 1. 将内容转换为LightRAG chunks格式
            lightrag_chunks = await self._convert_to_lightrag_chunks(content_list)
            
            # 2. 使用LightRAG的extract_entities函数
            chunk_results = await self._extract_entities_with_lightrag(lightrag_chunks)
            
            # 3. 处理结果并转换为标准格式
            entities, relationships = await self._process_chunk_results(chunk_results)
            
            # 4. 生成文档分析
            document_analysis = await self._analyze_document_structure(content_list)
            
            result = {
                'entities': entities,
                'relationships': relationships,
                'document_analysis': document_analysis,
                'statistics': {
                    'total_entities': len(entities),
                    'total_relationships': len(relationships),
                    'chunks_processed': len(lightrag_chunks),
                    'content_blocks_processed': len(content_list)
                }
            }
            
            logger.info(f"LightRAG实体提取完成: {len(entities)}个实体, {len(relationships)}个关系")
            return result
            
        except Exception as e:
            logger.error(f"LightRAG实体提取失败: {str(e)}")
            return {
                'entities': [],
                'relationships': [],
                'document_analysis': {},
                'statistics': {'error': str(e)}
            }
    
    async def _convert_to_lightrag_chunks(
        self, 
        content_list: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """将内容列表转换为LightRAG chunks格式"""
        lightrag_chunks = {}
        
        for i, item in enumerate(content_list):
            if not isinstance(item, dict):
                continue
            
            # 生成chunk ID
            content_text = self._extract_text_content(item)
            chunk_id = compute_mdhash_id(content_text, prefix="chunk-")
            
            # 构建chunk数据，格式与RAG-Anything一致
            chunk_data = {
                "content": content_text,
                "chunk_order_index": i,
                "full_doc_id": "ragcl-document",
                "chunk_index": i,
                "file_path": item.get("file_path", "unknown"),
                "page_idx": item.get("page_idx", 0),
                "content_type": item.get("type", "text"),
                "source_item": item
            }
            
            lightrag_chunks[chunk_id] = chunk_data
        
        return lightrag_chunks
    
    def _extract_text_content(self, item: Dict[str, Any]) -> str:
        """从内容项中提取文本"""
        content_type = item.get("type", "text")
        
        if content_type == "text":
            return item.get("text", "").strip()
        elif content_type == "table":
            # 处理表格内容
            caption = item.get("table_caption", "")
            body = item.get("table_body", [])
            
            text_parts = []
            if caption:
                text_parts.append(f"Table: {caption}")
            
            if body:
                for row in body[:5]:  # 限制行数
                    if isinstance(row, list):
                        row_text = " | ".join(str(cell)[:50] for cell in row[:8])  # 限制列数
                        text_parts.append(row_text)
            
            return "\n".join(text_parts)
        
        elif content_type == "image":
            # 处理图片内容
            caption = item.get("image_caption", "")
            return f"Image: {caption}" if caption else "Image content"
        
        else:
            # 通用处理
            return str(item.get("text", item.get("content", "")))[:500]
    
    async def _extract_entities_with_lightrag(
        self, 
        lightrag_chunks: Dict[str, Dict[str, Any]]
    ) -> List[Tuple]:
        """使用LightRAG的extract_entities函数"""
        try:
            # 获取pipeline状态
            pipeline_status = await get_namespace_data("pipeline_status")
            pipeline_status_lock = get_pipeline_status_lock()
            
            # 调用LightRAG的extract_entities函数
            chunk_results = await extract_entities(
                chunks=lightrag_chunks,
                global_config=self.lightrag.__dict__,
                pipeline_status=pipeline_status,
                pipeline_status_lock=pipeline_status_lock,
                llm_response_cache=self.lightrag.llm_response_cache,
                text_chunks_storage=self.lightrag.text_chunks,
            )
            
            return chunk_results
            
        except Exception as e:
            logger.error(f"LightRAG extract_entities调用失败: {str(e)}")
            return []
    
    async def _process_chunk_results(
        self, 
        chunk_results: List[Tuple]
    ) -> Tuple[List[Dict], List[Dict]]:
        """处理LightRAG的结果并转换为标准格式"""
        entities = []
        relationships = []
        
        for chunk_result in chunk_results:
            if len(chunk_result) >= 2:
                maybe_nodes, maybe_edges = chunk_result[0], chunk_result[1]
                
                # 处理节点（实体）
                if isinstance(maybe_nodes, dict):
                    for entity_name, entity_data in maybe_nodes.items():
                        if isinstance(entity_data, dict):
                            entity = {
                                "name": entity_name,
                                "type": entity_data.get("entity_type", "Entity"),
                                "description": entity_data.get("description", ""),
                                "relevance_score": 1.0,
                                "source_type": "lightrag",
                                "raw_data": entity_data
                            }
                            entities.append(entity)
                
                # 处理边（关系）
                if isinstance(maybe_edges, dict):
                    for edge_data in maybe_edges.values():
                        if isinstance(edge_data, dict):
                            relationship = {
                                "from": edge_data.get("src_id", ""),
                                "to": edge_data.get("tgt_id", ""),
                                "relation": edge_data.get("keywords", "related_to"),
                                "description": edge_data.get("description", ""),
                                "confidence": edge_data.get("weight", 1.0) / 10.0,
                                "raw_data": edge_data
                            }
                            relationships.append(relationship)
        
        return entities, relationships
    
    async def _analyze_document_structure(
        self, 
        content_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析文档结构"""
        # 统计内容类型
        content_types = {}
        pages = set()
        
        for item in content_list:
            if isinstance(item, dict):
                content_type = item.get("type", "unknown")
                content_types[content_type] = content_types.get(content_type, 0) + 1
                
                page_idx = item.get("page_idx")
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
    
    def extract_entities_sync(
        self, 
        content_list: List[Dict[str, Any]], 
        extract_relations: bool = True
    ) -> Dict[str, Any]:
        """同步版本的实体提取"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.extract_entities_from_content_list(content_list, extract_relations)
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


# 为了兼容性，创建一个适配器类
class EntityExtractor:
    """
    实体提取器适配器类
    
    保持与原有接口的兼容性，但内部使用LightRAG实现
    """
    
    def __init__(
        self,
        api_base: str = "https://api.chatanywhere.tech/v1",
        api_key: str = "sk-FiF5mSQ5EF1QrvI4FrVB7ZnrmXCjlJDUokJfTJ7HuNP5KQ78",
        model: str = "gpt-4o-mini"
    ):
        """初始化实体提取器"""
        config = LightRAGConfig(
            llm_api_base=api_base,
            llm_api_key=api_key,
            llm_model=model,
            embedding_api_base=api_base,
            embedding_api_key=api_key
        )
        
        self.lightrag_extractor = LightRAGEntityExtractor(config)
    
    async def extract_entities_from_content_list(
        self,
        content_list: List[Dict[str, Any]],
        extract_relations: bool = True
    ) -> Dict[str, Any]:
        """异步实体提取"""
        return await self.lightrag_extractor.extract_entities_from_content_list(
            content_list, extract_relations
        )
    
    def extract_entities_sync(
        self,
        content_list: List[Dict[str, Any]],
        extract_relations: bool = True
    ) -> Dict[str, Any]:
        """同步实体提取"""
        return self.lightrag_extractor.extract_entities_sync(
            content_list, extract_relations
        )