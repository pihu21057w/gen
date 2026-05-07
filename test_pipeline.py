#!/usr/bin/env python3
"""
Quick test of the dataset generation pipeline with minimal conversations
"""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import create_pipeline

def main():
    parser = argparse.ArgumentParser(description="Test dataset generation pipeline")
    parser.add_argument('--pdf', default='data/lech101.pdf', help='PDF file to process')
    parser.add_argument('--output', default='test_output.jsonl', help='Output JSONL file')
    parser.add_argument('--conversations', type=int, default=1, help='Number of conversations per doc (default: 1 for testing)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    print(f"🚀 Starting pipeline test")
    print(f"  PDF: {args.pdf}")
    print(f"  Output: {args.output}")
    print(f"  Conversations per doc: {args.conversations} (test mode)")
    print()
    
    try:
        # Create pipeline
        pipeline = create_pipeline('configs/config.yaml')
        
        # Override conversation count for testing
        pipeline.config['dataset']['num_conversations_per_doc'] = args.conversations
        pipeline.config['dataset']['output_file'] = args.output
        
        # Initialize components
        print("📦 Initializing pipeline components...")
        pipeline.initialize_model()
        pipeline.initialize_preprocessor()
        pipeline.initialize_dataset_generator()
        print()
        
        # Process document
        print(f"📄 Processing: {args.pdf}")
        conversations = pipeline.process_document(
            source=args.pdf,
            document_id=Path(args.pdf).stem
        )
        print()
        
        # Get stats
        stats = pipeline.get_stats()
        print(f"✅ Pipeline completed!")
        print(f"📊 Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        print()
        
        # Show sample
        print(f"📋 Sample entries from {args.output}:")
        try:
            with open(args.output, 'r') as f:
                for i, line in enumerate(f):
                    if i >= 2:  # Show first 2 entries
                        break
                    import json
                    entry = json.loads(line)
                    print(f"\n   Entry {i+1}:")
                    print(f"     Type: {entry.get('type')}")
                    print(f"     Document: {entry.get('document_id')}")
                    print(f"     Has reasoning: {entry.get('has_reasoning')}")
                    if 'conversations' in entry:
                        print(f"     Conversations: {len(entry['conversations'])} turns")
                        if entry['conversations']:
                            first_q = entry['conversations'][0].get('content', '')[:80]
                            print(f"     First Q: {first_q}...")
        except Exception as e:
            print(f"   Could not read sample: {str(e)}")
        
        print("\n✨ Test completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Pipeline interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
