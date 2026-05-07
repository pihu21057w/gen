"""
Main pipeline orchestrator
"""
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import json

from .logger_config import LoggerConfig
from .data_loaders import DataLoaderFactory
from .text_preprocessor import TextPreprocessor
from .llm_interface import LocalLLMInterface, ModelRecommendations
from .dataset_generator import DatasetGenerator

logger = logging.getLogger(__name__)


class DatasetPipeline:
    """Main pipeline for dataset generation"""
    
    def __init__(self, config_file: Union[str, Path]):
        """
        Initialize pipeline with configuration
        
        Args:
            config_file: Path to YAML configuration file
        """
        self.config_file = Path(config_file)
        self.config = None
        self.logger = None
        self.llm = None
        self.preprocessor = None
        self.dataset_generator = None
        self.checkpoint = {}
        
        self._load_config()
        self._setup_logging()
    
    def _load_config(self):
        """Load YAML configuration"""
        try:
            if not self.config_file.exists():
                raise FileNotFoundError(f"Config file not found: {self.config_file}")
            
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            
            print(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            raise
    
    def _setup_logging(self):
        """Setup logging configuration"""
        try:
            self.logger = LoggerConfig.setup_logger(
                config_file=self.config_file
            )
            self.logger.info("Pipeline initialized")
        except Exception as e:
            print(f"Error setting up logging: {str(e)}")
            raise
    
    def initialize_model(self, model_name: Optional[str] = None):
        """
        Initialize LLM model
        
        Args:
            model_name: Optional override for model name
        """
        try:
            model = model_name or self.config['model']['name']
            self.logger.info(f"Initializing model: {model}")
            
            self.llm = LocalLLMInterface(
                model_name=model,
                config=self.config['model']
            )
            
            model_info = self.llm.get_model_info()
            self.logger.info(f"Model info: {model_info}")
        
        except Exception as e:
            self.logger.error(f"Error initializing model: {str(e)}")
            raise
    
    def initialize_preprocessor(self):
        """Initialize text preprocessor"""
        try:
            self.preprocessor = TextPreprocessor(
                config=self.config.get('processing', {})
            )
            self.logger.info("Text preprocessor initialized")
        except Exception as e:
            self.logger.error(f"Error initializing preprocessor: {str(e)}")
            raise
    
    def initialize_dataset_generator(self):
        """Initialize dataset generator"""
        try:
            output_file = self.config['dataset']['output_file']
            prompts_file = self.config['dataset'].get('prompts_file', 'prompts.yaml')
            
            self.dataset_generator = DatasetGenerator(
                llm_interface=self.llm,
                output_file=output_file,
                prompts_file=prompts_file,
                config=self.config
            )
            self.logger.info(f"Dataset generator initialized (output: {output_file}, prompts: {prompts_file})")
        except Exception as e:
            self.logger.error(f"Error initializing dataset generator: {str(e)}")
            raise
    
    def process_document(
        self,
        source: Union[str, Path],
        document_id: Optional[str] = None,
        num_conversations: Optional[int] = None
    ) -> int:
        """
        Process a single document
        
        Args:
            source: Path to file or URL
            document_id: Optional document identifier
            num_conversations: Number of conversations to generate
            
        Returns:
            Number of conversations generated
        """
        try:
            # Set defaults
            if document_id is None:
                document_id = str(Path(source).stem if isinstance(source, (str, Path)) else source)
            
            if num_conversations is None:
                num_conversations = self.config['dataset']['num_conversations_per_doc']
            
            self.logger.info(f"Processing document: {source}")
            
            # Load document
            text = DataLoaderFactory.load_document(
                source,
                config=self.config
            )
            
            # Preprocess text
            processed = self.preprocessor.process_document(
                text,
                min_length=self.config['processing'].get('min_text_length', 100)
            )
            
            if processed is None:
                self.logger.warning(f"Document too short after processing: {source}")
                return 0
            
            # Generate conversations with smart chunking and preprocessor
            self.logger.info(f"Generating {num_conversations} conversations from document")
            
            conversations_added = self.dataset_generator.add_document(
                document_id=document_id,
                text=processed['cleaned_text'],
                source=str(source),
                num_conversations=num_conversations,
                preprocessor=self.preprocessor  # Pass preprocessor for smart chunking
            )
            
            # Save checkpoint
            self._save_checkpoint(document_id, source)
            
            return conversations_added
        
        except Exception as e:
            self.logger.error(f"Error processing document {source}: {str(e)}")
            return 0
    
    def process_documents_batch(
        self,
        sources: List[Union[str, Path]],
        num_conversations_per_doc: Optional[int] = None
    ) -> Dict:
        """
        Process multiple documents
        
        Args:
            sources: List of document sources
            num_conversations_per_doc: Number of conversations per document
            
        Returns:
            Statistics dictionary
        """
        try:
            stats = {
                'total_documents': len(sources),
                'successful': 0,
                'failed': 0,
                'total_conversations': 0,
                'start_time': datetime.now().isoformat(),
            }
            
            for i, source in enumerate(sources, 1):
                try:
                    self.logger.info(f"Processing document {i}/{len(sources)}")
                    conversations = self.process_document(
                        source,
                        num_conversations=num_conversations_per_doc
                    )
                    
                    if conversations > 0:
                        stats['successful'] += 1
                        stats['total_conversations'] += conversations
                    else:
                        stats['failed'] += 1
                
                except Exception as e:
                    self.logger.error(f"Failed to process document {source}: {str(e)}")
                    stats['failed'] += 1
            
            stats['end_time'] = datetime.now().isoformat()
            stats['dataset_stats'] = self.dataset_generator.get_dataset_stats()
            
            return stats
        
        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            return {}
    
    def _save_checkpoint(self, document_id: str, source: Union[str, Path]):
        """Save processing checkpoint"""
        try:
            checkpoint_file = Path(self.config['dataset']['output_file']).stem + "_checkpoint.json"
            
            self.checkpoint = {
                'last_document_id': document_id,
                'last_source': str(source),
                'timestamp': datetime.now().isoformat(),
                'total_conversations': self.dataset_generator.dataset_count,
            }
            
            with open(checkpoint_file, 'w') as f:
                json.dump(self.checkpoint, f, indent=2)
            
            self.logger.debug(f"Checkpoint saved: {checkpoint_file}")
        except Exception as e:
            self.logger.warning(f"Could not save checkpoint: {str(e)}")
    
    def get_status(self) -> Dict:
        """Get current pipeline status"""
        try:
            status = {
                'initialized': self.llm is not None,
                'model': self.llm.model_name if self.llm else None,
                'dataset_entries': self.dataset_generator.dataset_count if self.dataset_generator else 0,
                'output_file': self.config['dataset']['output_file'],
                'checkpoint': self.checkpoint,
            }
            
            return status
        except Exception as e:
            self.logger.error(f"Error getting status: {str(e)}")
            return {}
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.llm:
                self.llm.unload()
            self.logger.info("Pipeline cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")


# Convenience functions
def print_model_recommendations():
    """Print all model recommendations"""
    ModelRecommendations.print_recommendations()


def create_pipeline(config_file: Union[str, Path]) -> DatasetPipeline:
    """
    Create and initialize a pipeline
    
    Args:
        config_file: Path to configuration YAML file
        
    Returns:
        Initialized DatasetPipeline instance
    """
    pipeline = DatasetPipeline(config_file)
    pipeline.initialize_model()
    pipeline.initialize_preprocessor()
    pipeline.initialize_dataset_generator()
    return pipeline
