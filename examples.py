"""
Example: Using the pipeline programmatically
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import DatasetPipeline
from src.utils import DatasetStatistics, JSONLHandler


def example_basic_usage():
    """Basic usage example"""
    print("="*70)
    print("EXAMPLE 1: Basic Usage")
    print("="*70)
    
    # Initialize pipeline
    pipeline = DatasetPipeline('configs/config.yaml')
    pipeline.initialize_model()
    pipeline.initialize_preprocessor()
    pipeline.initialize_dataset_generator()
    
    # Process a single document
    pipeline.process_document(
        source='data/sample.pdf',
        document_id='doc1',
        num_conversations=3
    )
    
    # Show status
    status = pipeline.get_status()
    print(f"\nDataset Entries: {status['dataset_entries']}")
    print(f"Output File: {status['output_file']}")
    
    pipeline.cleanup()


def example_batch_processing():
    """Batch processing example"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Batch Processing")
    print("="*70)
    
    pipeline = DatasetPipeline('configs/config.yaml')
    pipeline.initialize_model()
    pipeline.initialize_preprocessor()
    pipeline.initialize_dataset_generator()
    
    # Process multiple documents
    sources = [
        'data/document1.pdf',
        'data/document2.txt',
        'data/document3.md',
    ]
    
    stats = pipeline.process_documents_batch(
        sources,
        num_conversations_per_doc=5
    )
    
    print(f"\nProcessed {stats['successful']} documents successfully")
    print(f"Generated {stats['total_conversations']} conversations")
    
    pipeline.cleanup()


def example_url_processing():
    """Process content from URLs"""
    print("\n" + "="*70)
    print("EXAMPLE 3: URL Processing")
    print("="*70)
    
    pipeline = DatasetPipeline('configs/config.yaml')
    pipeline.initialize_model()
    pipeline.initialize_preprocessor()
    pipeline.initialize_dataset_generator()
    
    # Process web content
    urls = [
        'https://en.wikipedia.org/wiki/Machine_learning',
        'https://example.com/article',
    ]
    
    for url in urls:
        try:
            pipeline.process_document(
                source=url,
                document_id=f"web_{url.split('/')[-1]}",
                num_conversations=3
            )
        except Exception as e:
            print(f"Failed to process {url}: {str(e)}")
    
    pipeline.cleanup()


def example_statistics():
    """Show dataset statistics"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Dataset Statistics")
    print("="*70)
    
    dataset_file = Path('outputs/generated_dataset.jsonl')
    
    if dataset_file.exists():
        DatasetStatistics.print_stats(dataset_file)
    else:
        print("Dataset file not found. Generate data first.")


def example_custom_config():
    """Use custom configuration"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Custom Configuration")
    print("="*70)
    
    # You can create multiple config files for different scenarios
    # e.g., configs/config_3b.yaml, configs/config_7b.yaml
    
    pipeline = DatasetPipeline('configs/config.yaml')
    
    # Override specific settings
    pipeline.config['model']['name'] = 'meta-llama/Llama-2-3b-hf'
    pipeline.config['dataset']['num_conversations_per_doc'] = 10
    
    pipeline.initialize_model()
    pipeline.initialize_preprocessor()
    pipeline.initialize_dataset_generator()
    
    # Process documents with custom config
    pipeline.process_document('data/sample.pdf', num_conversations=5)
    
    pipeline.cleanup()


if __name__ == '__main__':
    print("\n" + "="*70)
    print("DATASET GENERATION PIPELINE - EXAMPLES")
    print("="*70)
    print("\nNote: These examples require:")
    print("1. Configured LLM model (download from Hugging Face)")
    print("2. Sample data in 'data/' directory")
    print("3. Required dependencies installed")
    print("\nUncomment the example you want to run:\n")
    
    # Uncomment to run examples:
    # example_basic_usage()
    # example_batch_processing()
    # example_url_processing()
    # example_statistics()
    # example_custom_config()
    
    print("See source code for available examples.")
