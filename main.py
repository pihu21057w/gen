"""
Main entry point for dataset generation pipeline
"""
import sys
import argparse
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import create_pipeline, print_model_recommendations
from src.utils import DatasetStatistics, DataQualityChecker, JSONLHandler
from src.logger_config import LoggerConfig

logger = LoggerConfig.setup_logger()


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='Professional Dataset Generation Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate dataset from PDF
  python main.py --source data/document.pdf --output outputs/dataset.jsonl
  
  # Process multiple documents
  python main.py --source data/ --output outputs/dataset.jsonl
  
  # Show model recommendations
  python main.py --recommendations
  
  # Check dataset statistics
  python main.py --stats outputs/dataset.jsonl
  
  # Validate dataset quality
  python main.py --validate outputs/dataset.jsonl
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='configs/config.yaml',
        help='Path to configuration YAML file'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        help='Path to document or directory with documents (pdf, txt, md, or URL)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output JSONL file path'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        help='Override model name from config'
    )
    
    parser.add_argument(
        '--custom-prompt',
        type=str,
        help='Custom prompt for conversation (use {text} for content placeholder)'
    )
    
    parser.add_argument(
        '--cot-only',
        action='store_true',
        help='Generate only Chain-of-Thought conversations'
    )
    
    parser.add_argument(
        '--recommendations',
        action='store_true',
        help='Show model recommendations and exit'
    )
    
    parser.add_argument(
        '--stats',
        type=str,
        help='Show statistics for JSONL dataset'
    )
    
    parser.add_argument(
        '--validate',
        type=str,
        help='Validate quality of JSONL dataset'
    )
    
    parser.add_argument(
        '--conversations',
        type=int,
        default=5,
        help='Number of conversations per document'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Process documents in batch mode'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Show recommendations
    if args.recommendations:
        print_model_recommendations()
        return 0
    
    # Show statistics
    if args.stats:
        DatasetStatistics.print_stats(Path(args.stats))
        return 0
    
    # Validate dataset
    if args.validate:
        report = DataQualityChecker.check_dataset_quality(Path(args.validate))
        print("\n" + "="*70)
        print("DATASET QUALITY REPORT")
        print("="*70)
        print(f"Total Entries Checked: {report.get('total_checked')}")
        print(f"Valid Entries: {report.get('valid_entries')} ({report.get('valid_percentage'):.1f}%)")
        if report.get('issues'):
            print("\nIssues Found:")
            for issue, count in report['issues'].items():
                print(f"  {issue}: {count}")
        print("="*70 + "\n")
        return 0
    
    # Process documents
    if not args.source:
        parser.print_help()
        return 1
    
    try:
        logger.info("Starting dataset generation pipeline")
        
        # Create and initialize pipeline
        pipeline = create_pipeline(args.config)
        
        # Override model if specified
        if args.model:
            pipeline.initialize_model(args.model)
        
        # Override output file if specified
        if args.output:
            pipeline.config['dataset']['output_file'] = args.output
            pipeline.initialize_dataset_generator()
        
        # Apply custom prompts if specified
        if args.custom_prompt:
            pipeline.config['llm_prompts']['multi_turn_explanation'] = args.custom_prompt
            pipeline.dataset_generator.conv_generator.custom_prompts = pipeline.config.get('llm_prompts', {})
        
        # Force COT only if specified
        if args.cot_only:
            pipeline.config['conversation']['force_cot_entry'] = True
            pipeline.config['conversation']['cot_percentage'] = 1.0
        
        # Get source documents
        source_path = Path(args.source)
        sources = []
        
        if source_path.is_file():
            sources = [source_path]
        elif source_path.is_dir():
            # Find all supported formats
            supported = ['*.pdf', '*.txt', '*.md', '*.markdown']
            for pattern in supported:
                sources.extend(source_path.glob(pattern))
        else:
            logger.error(f"Source not found: {args.source}")
            return 1
        
        if not sources:
            logger.error(f"No supported documents found in {args.source}")
            return 1
        
        logger.info(f"Found {len(sources)} document(s) to process")
        
        # Process documents
        if args.batch or len(sources) > 1:
            logger.info("Processing in batch mode")
            stats = pipeline.process_documents_batch(
                sources,
                num_conversations_per_doc=args.conversations
            )
            
            print("\n" + "="*70)
            print("BATCH PROCESSING SUMMARY")
            print("="*70)
            print(f"Total Documents: {stats.get('total_documents')}")
            print(f"Successful: {stats.get('successful')}")
            print(f"Failed: {stats.get('failed')}")
            print(f"Total Conversations Generated: {stats.get('total_conversations')}")
            if stats.get('dataset_stats'):
                ds_stats = stats['dataset_stats']
                print(f"Dataset File: {ds_stats.get('output_file')}")
                print(f"File Size: {ds_stats.get('file_size_mb'):.2f} MB")
            print("="*70 + "\n")
        else:
            conversations = pipeline.process_document(
                sources[0],
                num_conversations=args.conversations
            )
            print(f"\nGenerated {conversations} conversations from document")
        
        # Show final status
        status = pipeline.get_status()
        print(f"\nDataset Location: {status['output_file']}")
        print(f"Total Entries: {status['dataset_entries']}")
        
        pipeline.cleanup()
        logger.info("Pipeline completed successfully")
        return 0
    
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
