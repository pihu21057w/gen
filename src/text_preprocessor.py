"""
Text preprocessing and cleaning module with smart chunking and problem detection
"""
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import html
import logging

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """Clean and preprocess text from various sources"""
    
    # Regex patterns
    URL_PATTERN = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
    MULTIPLE_SPACES_PATTERN = re.compile(r'\s{2,}')
    MULTIPLE_NEWLINES_PATTERN = re.compile(r'\n{3,}')
    IMAGE_MARKDOWN_PATTERN = re.compile(r'!\[.*?\]\(.*?\)')
    LINK_MARKDOWN_PATTERN = re.compile(r'\[.*?\]\((http|ftp)[^)]*\)')
    
    # Problem detection patterns
    MATH_PROBLEM_PATTERN = re.compile(
        r'(solve|find|calculate|prove|derive|show that|simplify)'
        r'.*?(quadratic|equation|integral|derivative|limit|series|matrix|vector|polynomial)',
        re.IGNORECASE
    )
    PHYSICS_PROBLEM_PATTERN = re.compile(
        r'(velocity|acceleration|force|energy|momentum|work|power|gravity|Newton|Coulomb|wave|frequency)',
        re.IGNORECASE
    )
    CHEMISTRY_PROBLEM_PATTERN = re.compile(
        r'(molecular|atom|element|bond|reaction|oxidation|pH|concentration|mole|equilibrium|compound)',
        re.IGNORECASE
    )
        
        # Smart chunking configuration
        self.use_smart_chunking = self.config.get('use_smart_chunking', True)
        self.chunk_strategy = self.config.get('chunk_strategy', 'semantic')
        self.preserve_boundaries = self.config.get('preserve_concept_boundaries', True)
        self.concept_keywords = self.config.get('concept_keywords', [])
        self.min_chunk_size = self.config.get('min_chunk_size', 200)
        
        # Problem detection
        self.detect_problems = self.config.get('detect_problems', True)
        self.problem_types = self.config.get('problem_types', [])
    BIOLOGY_PROBLEM_PATTERN = re.compile(
        r'(cell|DNA|RNA|protein|enzyme|photosynthesis|respiration|evolution|genetic|organism)',
        re.IGNORECASE
    )
    QUESTION_PATTERN = re.compile(r'^\s*([0-9]+[\.\)]\s+)?(.+\?)', re.MULTILINE)
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize preprocessor with configuration
        
        Args:
            config: Dictionary with preprocessing settings
        """
        self.config = config or {}
        self.remove_urls = self.config.get('remove_urls', True)
        self.remove_emails = self.config.get('remove_emails', True)
        self.remove_html = self.config.get('remove_html_tags', True)
        self.remove_images = self.config.get('remove_images', True)
        self.remove_code_blocks = self.config.get('remove_code_blocks', False)
        self.keep_math = self.config.get('keep_math', True)
    
    def clean(self, text: str) -> str:
        """
        Clean text by removing unwanted elements
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        text = html.unescape(text)
        
        # Remove HTML tags
        if self.remove_html:
            text = self.HTML_TAG_PATTERN.sub('', text)
        
        # Remove images (markdown format)
        if self.remove_images:
            text = self.IMAGE_MARKDOWN_PATTERN.sub('', text)
        
        # Remove URLs (but preserve text in links if it's markdown)
        if self.remove_urls:
            # Remove plain URLs
            text = self.URL_PATTERN.sub('', text)
            # Remove Markdown links but keep the text
            text = re.sub(r'\[(.*?)\]\((http|ftp)[^)]*\)', r'\1', text)
        
        # Remove emails
        if self.remove_emails:
            text = self.EMAIL_PATTERN.sub('', text)
        
        # Remove code blocks (markdown)
        if self.remove_code_blocks:
            text = re.sub(r'```[\s\S]*?```', '', text)
            text = re.sub(r'`[^`]*`', '', text)
        
        # Remove multiple spaces
        text = self.MULTIPLE_SPACES_PATTERN.sub(' ', text)
        
        # Remove multiple newlines (keep max 2)
        text = self.MULTIPLE_NEWLINES_PATTERN.sub('\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 2000, 
        overlap: int = 200
    ) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between consecutive chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    def smart_chunk_text(
        self,
        text: str,
        chunk_size: int = 1500,
        overlap: int = 300
    ) -> List[Dict]:
        """
        Intelligently chunk text while preserving concept boundaries
        
        Args:
            text: Text to chunk
            chunk_size: Target size for each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of chunks with metadata
        """
        if len(text) <= chunk_size:
            return [{
                'content': text,
                'start': 0,
                'end': len(text),
                'problems': self.detect_problems_in_text(text) if self.detect_problems else []
            }]
        
        chunks = []
        paragraphs = self.extract_paragraphs(text)
        current_chunk = ""
        chunk_start = 0
        
        for para in paragraphs:
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append({
                    'content': current_chunk.strip(),
                    'start': chunk_start,
                    'end': chunk_start + len(current_chunk),
                    'problems': self.detect_problems_in_text(current_chunk) if self.detect_problems else []
                })
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + para
                chunk_start = max(0, chunk_start + len(current_chunk) - len(overlap_text) - overlap)
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Add remaining content
        if current_chunk.strip():
            chunks.append({
                'content': current_chunk.strip(),
                'start': chunk_start,
                'end': chunk_start + len(current_chunk),
                'problems': self.detect_problems_in_text(current_chunk) if self.detect_problems else []
            })
        
        # Filter very small chunks
        chunks = [c for c in chunks if len(c['content']) >= self.min_chunk_size]
        
        logger.info(f"Smart chunked text into {len(chunks)} chunks (avg size: {len(text)//len(chunks) if chunks else 0})")
        return chunks
    
    def detect_problems_in_text(self, text: str) -> List[Dict]:
        """
        Detect mathematical, physics, chemistry problems in text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected problems with type and content
        """
        problems = []
        
        # Extract questions/problems
        questions = self.QUESTION_PATTERN.findall(text)
        
        for match in questions:
            question_text = match[1] if isinstance(match, tuple) else match
            
            problem_type = None
            
            # Detect problem type
            if self.MATH_PROBLEM_PATTERN.search(question_text):
                problem_type = "math"
            elif self.PHYSICS_PROBLEM_PATTERN.search(question_text):
                problem_type = "physics"
            elif self.CHEMISTRY_PROBLEM_PATTERN.search(question_text):
                problem_type = "chemistry"
            elif self.BIOLOGY_PROBLEM_PATTERN.search(question_text):
                problem_type = "biology"
            else:
                problem_type = "question"
            
            if problem_type in self.problem_types or not self.problem_types:
                problems.append({
                    'type': problem_type,
                    'content': question_text.strip(),
                    'requires_solving': problem_type in ['math', 'physics', 'chemistry', 'biology']
                })
        
        return problems
    
    def extract_problem_solution_pair(self, text: str) -> Optional[Tuple[str, str]]:
        """
        Extract problem-solution pairs from text
        
        Args:
            text: Text containing problem and solution
            
        Returns:
            Tuple of (problem, solution) or None
        """
        # Find question
        question_match = self.QUESTION_PATTERN.search(text)
        if not question_match:
            return None
        
        question = question_match.group(0)
        
        # Find solution (text after question, before next question)
        next_question = self.QUESTION_PATTERN.search(text, question_match.end())
        if next_question:
            solution = text[question_match.end():next_question.start()].strip()
        else:
            solution = text[question_match.end():].strip()
        
        if solution and len(solution) > 20:
            return (question.strip(), solution.strip())
        
        return None
    
    def extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text
        
        Args:
            text: Text to extract sentences from
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting on . ! ?
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def extract_paragraphs(self, text: str) -> List[str]:
        """
        Extract paragraphs from text
        
        Args:
            text: Text to extract paragraphs from
            
        Returns:
            List of paragraphs
        """
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        return paragraphs
    
    def is_math_expression(self, text: str) -> bool:
        """
        Check if text contains mathematical expressions
        
        Args:
            text: Text to check
            
        Returns:
            True if contains math expressions
        """
        math_patterns = [
            r'\$.*?\$',  # LaTeX inline
            r'\\\(.*?\\\)',  # Alternative LaTeX
            r'∑|∏|∫|√|∞|∝|≈|≠|±|×|÷',  # Math symbols
            r'\b(sin|cos|tan|log|ln|exp|sqrt|abs)\(',  # Math functions
        ]
        
        for pattern in math_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def process_document(
        self, 
        text: str, 
        min_length: int = 100
    ) -> Optional[Dict]:
        """
        Process a complete document
        
        Args:
            text: Document text
            min_length: Minimum text length to process
            
        Returns:
            Dictionary with processed content or None if too short
        """
        # Clean text
        cleaned = self.clean(text)
        
        if len(cleaned) < min_length:
            return None
        
        # Extract content
        paragraphs = self.extract_paragraphs(cleaned)
        sentences = self.extract_sentences(cleaned)
        chunks = self.chunk_text(
            cleaned,
            chunk_size=self.config.get('chunk_size', 2000),
            overlap=self.config.get('chunk_overlap', 200)
        )
        
        return {
            'original_length': len(text),
            'cleaned_length': len(cleaned),
            'cleaned_text': cleaned,
            'paragraphs': paragraphs,
            'sentences': sentences,
            'chunks': chunks,
            'has_math': self.keep_math and self.is_math_expression(cleaned),
        }
