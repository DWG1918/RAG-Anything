"""
RAG-CL Main Module

This module provides the main RAGAnythingCL class that orchestrates document parsing
using the parser components extracted from RAG-Anything.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from .config import RAGAnythingCLConfig
from .parser import MineruParser, DoclingParser, Parser


class RAGAnythingCL:
    """
    Main RAG-CL class that provides document parsing functionality
    
    This class serves as the main interface for the RAG-CL system,
    utilizing the document parsing capabilities extracted from RAG-Anything.
    """
    
    def __init__(self, config: Optional[RAGAnythingCLConfig] = None):
        """
        Initialize RAG-CL system
        
        Args:
            config: Configuration object. If None, default configuration is used.
        """
        self.config = config or RAGAnythingCLConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize parser based on configuration
        self.parser = self._init_parser()
        
        # Ensure working directory exists
        Path(self.config.working_dir).mkdir(parents=True, exist_ok=True)
    
    def _init_parser(self) -> Parser:
        """
        Initialize the document parser based on configuration
        
        Returns:
            Parser: Configured parser instance
        """
        if self.config.parser == "mineru":
            parser = MineruParser()
        elif self.config.parser == "docling":
            parser = DoclingParser()
        else:
            raise ValueError(f"Unsupported parser: {self.config.parser}")
        
        # Check if parser is properly installed
        if not parser.check_installation():
            self.logger.warning(f"{self.config.parser} installation check failed")
        
        return parser
    
    def parse_document(
        self,
        file_path: Union[str, Path],
        output_dir: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Parse a single document
        
        Args:
            file_path: Path to the document file
            output_dir: Output directory (uses config working_dir if None)
            **kwargs: Additional arguments for parser
            
        Returns:
            List[Dict[str, Any]]: Parsed content blocks
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        # Use configured output directory if not specified
        if output_dir is None:
            output_dir = self.config.working_dir
        
        # Merge configuration kwargs with provided kwargs
        parser_kwargs = self.config.get_parser_kwargs()
        parser_kwargs.update(kwargs)
        
        self.logger.info(f"Parsing document: {file_path}")
        
        try:
            content_list = self.parser.parse_document(
                file_path=file_path,
                method=self.config.parse_method,
                output_dir=output_dir,
                lang=self.config.document_language,
                **parser_kwargs
            )
            
            self.logger.info(f"Successfully parsed {file_path}: {len(content_list)} content blocks")
            
            # Save results if configured
            if self.config.save_intermediate:
                self._save_results(file_path, content_list, output_dir)
            
            return content_list
            
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {str(e)}")
            raise
    
    def parse_documents_batch(
        self,
        file_paths: List[Union[str, Path]],
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse multiple documents in batch
        
        Args:
            file_paths: List of file paths to parse
            output_dir: Output directory (uses config working_dir if None)
            **kwargs: Additional arguments for parser
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Mapping of file paths to parsed content
        """
        if output_dir is None:
            output_dir = self.config.working_dir
        
        results = {}
        failed_files = []
        
        # Process files in batches
        batch_size = self.config.batch_size
        max_workers = self.config.max_workers
        
        self.logger.info(f"Processing {len(file_paths)} documents in batches of {batch_size}")
        
        # Split into batches
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} files")
            
            # Process batch with thread pool
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit tasks
                future_to_path = {
                    executor.submit(self.parse_document, file_path, output_dir, **kwargs): file_path
                    for file_path in batch
                }
                
                # Collect results
                for future in as_completed(future_to_path):
                    file_path = future_to_path[future]
                    try:
                        content_list = future.result()
                        results[str(file_path)] = content_list
                    except Exception as e:
                        self.logger.error(f"Failed to parse {file_path}: {str(e)}")
                        failed_files.append(str(file_path))
        
        # Report results
        success_count = len(results)
        failure_count = len(failed_files)
        total_count = len(file_paths)
        
        self.logger.info(
            f"Batch processing complete: {success_count}/{total_count} successful, "
            f"{failure_count} failed"
        )
        
        if failed_files:
            self.logger.warning(f"Failed files: {failed_files}")
        
        return results
    
    def _save_results(
        self,
        file_path: Path,
        content_list: List[Dict[str, Any]],
        output_dir: str
    ) -> None:
        """
        Save parsing results to file
        
        Args:
            file_path: Original file path
            content_list: Parsed content blocks
            output_dir: Output directory
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create output filename
        base_name = file_path.stem
        
        if self.config.output_format == "json":
            output_file = output_path / f"{base_name}_parsed.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(content_list, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"Saved JSON results to {output_file}")
        
        elif self.config.output_format == "markdown":
            output_file = output_path / f"{base_name}_parsed.md"
            markdown_content = self._content_to_markdown(content_list)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            self.logger.debug(f"Saved Markdown results to {output_file}")
    
    def _content_to_markdown(self, content_list: List[Dict[str, Any]]) -> str:
        """
        Convert content list to markdown format
        
        Args:
            content_list: List of content blocks
            
        Returns:
            str: Markdown formatted content
        """
        markdown_lines = []
        
        for item in content_list:
            if not isinstance(item, dict):
                continue
            
            content_type = item.get("type", "unknown")
            
            if content_type == "text":
                text = item.get("text", "")
                markdown_lines.append(text)
                markdown_lines.append("")  # Empty line
            
            elif content_type == "image":
                caption = item.get("image_caption", "")
                img_path = item.get("img_path", "")
                if img_path:
                    markdown_lines.append(f"![{caption}]({img_path})")
                    if caption:
                        markdown_lines.append(f"*{caption}*")
                    markdown_lines.append("")
            
            elif content_type == "table":
                caption = item.get("table_caption", "")
                table_body = item.get("table_body", [])
                
                if caption:
                    markdown_lines.append(f"**Table: {caption}**")
                    markdown_lines.append("")
                
                if table_body and len(table_body) > 0:
                    # Simple table formatting
                    for row_idx, row in enumerate(table_body):
                        if isinstance(row, list):
                            row_str = " | ".join(str(cell) for cell in row)
                            markdown_lines.append(f"| {row_str} |")
                            
                            # Add separator after header row
                            if row_idx == 0:
                                separator = " | ".join("---" for _ in row)
                                markdown_lines.append(f"| {separator} |")
                    
                    markdown_lines.append("")
            
            elif content_type == "equation":
                text = item.get("text", "")
                markdown_lines.append(f"$$\n{text}\n$$")
                markdown_lines.append("")
        
        return "\n".join(markdown_lines)
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get supported file formats for the current parser
        
        Returns:
            Dict[str, List[str]]: Dictionary of format categories and extensions
        """
        formats = {
            "PDF": [".pdf"],
            "Images": list(Parser.IMAGE_FORMATS),
            "Text": list(Parser.TEXT_FORMATS),
        }
        
        if self.config.parser == "mineru":
            formats["Office"] = list(Parser.OFFICE_FORMATS) + [" (requires LibreOffice)"]
        elif self.config.parser == "docling":
            formats["Office"] = list(Parser.OFFICE_FORMATS)
            formats["HTML"] = list(DoclingParser.HTML_FORMATS)
        
        return formats
    
    def check_installation(self) -> bool:
        """
        Check if the parser is properly installed
        
        Returns:
            bool: True if installation is valid
        """
        return self.parser.check_installation()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current configuration
        
        Returns:
            Dict[str, Any]: Configuration summary
        """
        return {
            "parser": self.config.parser,
            "parse_method": self.config.parse_method,
            "working_dir": self.config.working_dir,
            "multimodal_processing": {
                "images": self.config.enable_image_processing,
                "tables": self.config.enable_table_processing,
                "equations": self.config.enable_equation_processing,
            },
            "batch_settings": {
                "batch_size": self.config.batch_size,
                "max_workers": self.config.max_workers,
            },
            "output_format": self.config.output_format,
            "supported_formats": self.get_supported_formats(),
        }