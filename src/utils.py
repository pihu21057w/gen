"""
Utility functions for the pipeline
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class JSONLHandler:
    """Handle JSONL file operations"""
    
    @staticmethod
    def read_jsonl(file_path: Path) -> List[Dict]:
        """
        Read JSONL file
        
        Args:
            file_path: Path to JSONL file
            
        Returns:
            List of dictionaries
        """
        try:
            data = []
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            logger.info(f"Read {len(data)} entries from {file_path}")
            return data
        except Exception as e:
            logger.error(f"Error reading JSONL file {file_path}: {str(e)}")
            return []
    
    @staticmethod
    def write_jsonl(file_path: Path, data: List[Dict], append: bool = True):
        """
        Write JSONL file
        
        Args:
            file_path: Path to JSONL file
            data: List of dictionaries
            append: Append to existing file or overwrite
        """
        try:
            mode = 'a' if append else 'w'
            with open(file_path, mode) as f:
                for item in data:
                    f.write(json.dumps(item) + '\n')
            logger.info(f"Written {len(data)} entries to {file_path}")
        except Exception as e:
            logger.error(f"Error writing JSONL file {file_path}: {str(e)}")
    
    @staticmethod
    def validate_jsonl(file_path: Path) -> bool:
        """
        Validate JSONL file format
        
        Args:
            file_path: Path to JSONL file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        json.loads(line)
            return True
        except Exception as e:
            logger.error(f"JSONL validation failed for {file_path}: {str(e)}")
            return False


class DatasetStatistics:
    """Calculate statistics about dataset"""
    
    @staticmethod
    def get_stats(file_path: Path) -> Dict[str, Any]:
        """
        Calculate dataset statistics
        
        Args:
            file_path: Path to JSONL dataset file
            
        Returns:
            Dictionary with statistics
        """
        try:
            data = JSONLHandler.read_jsonl(file_path)
            
            if not data:
                return {'error': 'Empty dataset'}
            
            # Count by type
            type_counts = {}
            template_counts = {}
            reasoning_count = 0
            
            for entry in data:
                conv_type = entry.get('type', 'unknown')
                type_counts[conv_type] = type_counts.get(conv_type, 0) + 1
                
                template = entry.get('template', 'unknown')
                template_counts[template] = template_counts.get(template, 0) + 1
                
                if entry.get('has_reasoning'):
                    reasoning_count += 1
            
            stats = {
                'total_entries': len(data),
                'file_size_mb': file_path.stat().st_size / (1024 * 1024),
                'by_type': type_counts,
                'by_template': template_counts,
                'with_reasoning': reasoning_count,
                'reasoning_percentage': (reasoning_count / len(data)) * 100 if data else 0,
                'unique_documents': len(set(e.get('document_id') for e in data)),
                'unique_sources': len(set(e.get('source') for e in data)),
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            return {}
    
    @staticmethod
    def print_stats(file_path: Path):
        """Print formatted statistics"""
        stats = DatasetStatistics.get_stats(file_path)
        
        if 'error' in stats:
            print(f"Error: {stats['error']}")
            return
        
        print("\n" + "="*70)
        print("DATASET STATISTICS")
        print("="*70)
        print(f"Total Entries: {stats['total_entries']}")
        print(f"File Size: {stats['file_size_mb']:.2f} MB")
        print(f"Unique Documents: {stats['unique_documents']}")
        print(f"Unique Sources: {stats['unique_sources']}")
        print(f"\nBy Type:")
        for conv_type, count in stats['by_type'].items():
            print(f"  {conv_type}: {count}")
        print(f"\nReasoning:")
        print(f"  Total with reasoning: {stats['with_reasoning']} ({stats['reasoning_percentage']:.1f}%)")
        print("="*70 + "\n")


class DataQualityChecker:
    """Check quality of generated dataset"""
    
    @staticmethod
    def check_entry_quality(entry: Dict) -> Dict[str, Any]:
        """
        Check quality of single entry
        
        Args:
            entry: JSONL entry
            
        Returns:
            Quality report
        """
        issues = []
        
        # Check required fields
        required_fields = ['dataset_id', 'document_id', 'type', 'conversations']
        for field in required_fields:
            if field not in entry:
                issues.append(f"Missing required field: {field}")
        
        # Check conversations
        conversations = entry.get('conversations', [])
        if len(conversations) < 2:
            issues.append("Less than 2 messages in conversation")
        
        # Check conversation format
        for i, msg in enumerate(conversations):
            if 'role' not in msg or 'content' not in msg:
                issues.append(f"Invalid message format at index {i}")
            if not msg.get('content') or len(msg.get('content', '')) < 10:
                issues.append(f"Empty or very short message at index {i}")
        
        # Check content length
        total_length = sum(len(msg.get('content', '')) for msg in conversations)
        if total_length < 50:
            issues.append("Total conversation too short")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'message_count': len(conversations),
            'total_content_length': total_length,
        }
    
    @staticmethod
    def check_dataset_quality(file_path: Path, sample_size: Optional[int] = None) -> Dict:
        """
        Check quality of entire dataset
        
        Args:
            file_path: Path to JSONL dataset
            sample_size: Number of entries to check (None = all)
            
        Returns:
            Quality report
        """
        try:
            data = JSONLHandler.read_jsonl(file_path)
            
            if not data:
                return {'error': 'Empty dataset'}
            
            # Sample if specified
            if sample_size and len(data) > sample_size:
                import random
                data = random.sample(data, sample_size)
            
            issues_by_type = {}
            valid_count = 0
            
            for entry in data:
                quality = DataQualityChecker.check_entry_quality(entry)
                
                if quality['valid']:
                    valid_count += 1
                else:
                    for issue in quality['issues']:
                        issues_by_type[issue] = issues_by_type.get(issue, 0) + 1
            
            report = {
                'total_checked': len(data),
                'valid_entries': valid_count,
                'valid_percentage': (valid_count / len(data)) * 100 if data else 0,
                'issues': issues_by_type,
            }
            
            return report
        except Exception as e:
            logger.error(f"Error checking dataset quality: {str(e)}")
            return {}
