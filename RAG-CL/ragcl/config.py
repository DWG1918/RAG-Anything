"""
RAG-CL Configuration Module

This module provides configuration classes for the RAG-CL system.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os
from pathlib import Path


@dataclass
class RAGAnythingCLConfig:
    """
    Configuration class for RAG-CL system
    
    This configuration supports both direct instantiation and environment variable fallbacks.
    Environment variables follow the pattern: RAG_CL_<FIELD_NAME> (uppercase)
    """
    
    # Basic configuration
    working_dir: str = field(
        default_factory=lambda: os.getenv("RAG_CL_WORKING_DIR", "./ragcl_data")
    )
    
    # Parser configuration
    parser: str = field(
        default_factory=lambda: os.getenv("RAG_CL_PARSER", "mineru")
    )
    parse_method: str = field(
        default_factory=lambda: os.getenv("RAG_CL_PARSE_METHOD", "auto")
    )
    
    # Document processing settings
    enable_ocr: bool = field(
        default_factory=lambda: os.getenv("RAG_CL_ENABLE_OCR", "true").lower() == "true"
    )
    
    # Multimodal processing toggles
    enable_image_processing: bool = field(
        default_factory=lambda: os.getenv("RAG_CL_ENABLE_IMAGE", "false").lower() == "true"
    )
    enable_table_processing: bool = field(
        default_factory=lambda: os.getenv("RAG_CL_ENABLE_TABLE", "false").lower() == "true"
    )
    enable_equation_processing: bool = field(
        default_factory=lambda: os.getenv("RAG_CL_ENABLE_EQUATION", "false").lower() == "true"
    )
    
    # Parser-specific settings
    mineru_backend: str = field(
        default_factory=lambda: os.getenv("RAG_CL_MINERU_BACKEND", "pipeline")
    )
    mineru_device: Optional[str] = field(
        default_factory=lambda: os.getenv("RAG_CL_MINERU_DEVICE")
    )
    mineru_source: str = field(
        default_factory=lambda: os.getenv("RAG_CL_MINERU_SOURCE", "huggingface")
    )
    
    # Language settings
    document_language: Optional[str] = field(
        default_factory=lambda: os.getenv("RAG_CL_DOCUMENT_LANGUAGE")
    )
    
    # Batch processing settings
    batch_size: int = field(
        default_factory=lambda: int(os.getenv("RAG_CL_BATCH_SIZE", "10"))
    )
    max_workers: int = field(
        default_factory=lambda: int(os.getenv("RAG_CL_MAX_WORKERS", "4"))
    )
    
    # Output settings
    output_format: str = field(
        default_factory=lambda: os.getenv("RAG_CL_OUTPUT_FORMAT", "json")
    )
    save_intermediate: bool = field(
        default_factory=lambda: os.getenv("RAG_CL_SAVE_INTERMEDIATE", "true").lower() == "true"
    )
    
    # Additional parser kwargs
    parser_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Ensure working directory exists
        Path(self.working_dir).mkdir(parents=True, exist_ok=True)
        
        # Validate parser selection
        if self.parser not in ["mineru", "docling"]:
            raise ValueError(f"Invalid parser: {self.parser}. Must be 'mineru' or 'docling'")
        
        # Validate parse method
        if self.parse_method not in ["auto", "txt", "ocr"]:
            raise ValueError(f"Invalid parse method: {self.parse_method}. Must be 'auto', 'txt', or 'ocr'")
        
        # Validate output format
        if self.output_format not in ["json", "markdown"]:
            raise ValueError(f"Invalid output format: {self.output_format}. Must be 'json' or 'markdown'")
    
    def get_parser_kwargs(self) -> Dict[str, Any]:
        """
        Get parser-specific keyword arguments
        
        Returns:
            Dict[str, Any]: Parser kwargs with appropriate filtering
        """
        kwargs = self.parser_kwargs.copy()
        
        if self.parser == "mineru":
            kwargs.update({
                "backend": self.mineru_backend,
                "device": self.mineru_device,
                "source": self.mineru_source,
                "formula": self.enable_equation_processing,
                "table": self.enable_table_processing,
            })
            # Remove None values
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        return kwargs
    
    @classmethod
    def from_env_file(cls, env_file: str = ".env") -> "RAGAnythingCLConfig":
        """
        Create configuration from environment file
        
        Args:
            env_file: Path to environment file
            
        Returns:
            RAGAnythingCLConfig: Configuration instance
        """
        env_path = Path(env_file)
        if env_path.exists():
            # Simple env file parsing (can be enhanced with python-dotenv)
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, _, value = line.partition('=')
                        os.environ[key.strip()] = value.strip()
        
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary
        
        Returns:
            Dict[str, Any]: Configuration as dictionary
        """
        return {
            "working_dir": self.working_dir,
            "parser": self.parser,
            "parse_method": self.parse_method,
            "enable_ocr": self.enable_ocr,
            "enable_image_processing": self.enable_image_processing,
            "enable_table_processing": self.enable_table_processing,
            "enable_equation_processing": self.enable_equation_processing,
            "mineru_backend": self.mineru_backend,
            "mineru_device": self.mineru_device,
            "mineru_source": self.mineru_source,
            "document_language": self.document_language,
            "batch_size": self.batch_size,
            "max_workers": self.max_workers,
            "output_format": self.output_format,
            "save_intermediate": self.save_intermediate,
            "parser_kwargs": self.parser_kwargs,
        }