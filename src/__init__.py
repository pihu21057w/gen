"""
Dataset Generation Pipeline Package
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Professional dataset generation pipeline for fine-tuning using local LLMs"

from .logger_config import LoggerConfig, get_logger
from .text_preprocessor import TextPreprocessor
from .data_loaders import DataLoaderFactory
from .llm_interface import LocalLLMInterface, ModelRecommendations
from .dataset_generator import ConversationGenerator, DatasetGenerator
from .pipeline import DatasetPipeline, create_pipeline, print_model_recommendations
from .utils import JSONLHandler, DatasetStatistics, DataQualityChecker

__all__ = [
    'LoggerConfig',
    'get_logger',
    'TextPreprocessor',
    'DataLoaderFactory',
    'LocalLLMInterface',
    'ModelRecommendations',
    'ConversationGenerator',
    'DatasetGenerator',
    'DatasetPipeline',
    'create_pipeline',
    'print_model_recommendations',
    'JSONLHandler',
    'DatasetStatistics',
    'DataQualityChecker',
]
