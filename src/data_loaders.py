"""
Data loaders for various document formats
"""
import re
from pathlib import Path
from typing import Optional, Dict, List, Union
from abc import ABC, abstractmethod
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class BaseLoader(ABC):
    """Base class for all data loaders"""
    
    @abstractmethod
    def load(self, source: Union[str, Path]) -> str:
        """Load data from source and return text"""
        pass
    
    def validate_source(self, source: Union[str, Path]) -> bool:
        """Validate if source is accessible"""
        return True


class TextLoader(BaseLoader):
    """Load plain text files"""
    
    def load(self, source: Union[str, Path]) -> str:
        """Load text file"""
        try:
            source = Path(source)
            if not source.exists():
                raise FileNotFoundError(f"File not found: {source}")
            
            with open(source, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"Loaded text file: {source} ({len(text)} chars)")
            return text
        except Exception as e:
            logger.error(f"Error loading text file {source}: {str(e)}")
            raise


class PDFLoader(BaseLoader):
    """Load PDF files"""
    
    def __init__(self, use_ocr: bool = False):
        """
        Initialize PDF loader
        
        Args:
            use_ocr: Use OCR for scanned PDFs (requires pytesseract)
        """
        self.use_ocr = use_ocr
        self._import_dependencies()
    
    def _import_dependencies(self):
        """Import required PDF libraries"""
        try:
            import PyPDF2
            self.PyPDF2 = PyPDF2
        except ImportError:
            raise ImportError("PyPDF2 not installed. Install: pip install PyPDF2")
        
        if self.use_ocr:
            try:
                import pytesseract
                from PIL import Image
                self.pytesseract = pytesseract
                self.Image = Image
            except ImportError:
                raise ImportError(
                    "pytesseract or PIL not installed. Install: pip install pytesseract pillow"
                )
    
    def load(self, source: Union[str, Path]) -> str:
        """
        Load PDF file
        
        Args:
            source: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            source = Path(source)
            if not source.exists():
                raise FileNotFoundError(f"PDF file not found: {source}")
            
            text = ""
            
            with open(source, 'rb') as f:
                pdf_reader = self.PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
                    text += "\n\n"
            
            logger.info(f"Loaded PDF: {source} ({num_pages} pages, {len(text)} chars)")
            return text
        except Exception as e:
            logger.error(f"Error loading PDF {source}: {str(e)}")
            raise


class MarkdownLoader(BaseLoader):
    """Load Markdown files"""
    
    def load(self, source: Union[str, Path]) -> str:
        """Load markdown file"""
        try:
            source = Path(source)
            if not source.exists():
                raise FileNotFoundError(f"File not found: {source}")
            
            with open(source, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"Loaded markdown file: {source} ({len(text)} chars)")
            return text
        except Exception as e:
            logger.error(f"Error loading markdown file {source}: {str(e)}")
            raise


class URLLoader(BaseLoader):
    """Load content from URLs"""
    
    def __init__(self, timeout: int = 30, headers: Optional[Dict] = None):
        """
        Initialize URL loader
        
        Args:
            timeout: Request timeout in seconds
            headers: HTTP headers to use
        """
        self.timeout = timeout
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self._import_dependencies()
    
    def _import_dependencies(self):
        """Import required libraries"""
        try:
            import requests
            from bs4 import BeautifulSoup
            self.requests = requests
            self.BeautifulSoup = BeautifulSoup
        except ImportError:
            raise ImportError(
                "requests or beautifulsoup4 not installed. "
                "Install: pip install requests beautifulsoup4"
            )
    
    def load(self, source: str, retry_attempts: int = 3) -> str:
        """
        Load content from URL
        
        Args:
            source: URL to load
            retry_attempts: Number of retry attempts
            
        Returns:
            Extracted text content
        """
        if not self._is_valid_url(source):
            raise ValueError(f"Invalid URL: {source}")
        
        for attempt in range(retry_attempts):
            try:
                response = self.requests.get(
                    source,
                    timeout=self.timeout,
                    headers=self.headers
                )
                response.raise_for_status()
                
                # Parse HTML
                soup = self.BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style tags
                for tag in soup(['script', 'style', 'nav', 'footer']):
                    tag.decompose()
                
                # Extract text
                text = soup.get_text(separator='\n', strip=True)
                
                logger.info(f"Loaded URL: {source} ({len(text)} chars)")
                return text
            
            except self.requests.RequestException as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{retry_attempts} failed for {source}: {str(e)}"
                )
                if attempt == retry_attempts - 1:
                    logger.error(f"Failed to load URL after {retry_attempts} attempts")
                    raise
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False


class DataLoaderFactory:
    """Factory for creating appropriate data loaders"""
    
    # Supported formats and their loaders
    LOADERS = {
        'txt': TextLoader,
        'md': MarkdownLoader,
        'markdown': MarkdownLoader,
        'pdf': PDFLoader,
    }
    
    @classmethod
    def get_loader(cls, source: Union[str, Path], config: Optional[Dict] = None) -> BaseLoader:
        """
        Get appropriate loader for data source
        
        Args:
            source: Path or URL to load
            config: Configuration dictionary
            
        Returns:
            Appropriate data loader instance
        """
        config = config or {}
        
        # Check if it's a URL
        if isinstance(source, str) and (source.startswith('http://') or source.startswith('https://')):
            web_config = config.get('web', {})
            return URLLoader(
                timeout=web_config.get('timeout', 30),
                headers=web_config.get('headers', {})
            )
        
        # Check if it's a file
        source_path = Path(source)
        if source_path.exists():
            suffix = source_path.suffix.lstrip('.').lower()
            if suffix in cls.LOADERS:
                loader_class = cls.LOADERS[suffix]
                if suffix == 'pdf':
                    pdf_config = config.get('pdf', {})
                    return loader_class(use_ocr=pdf_config.get('use_ocr', False))
                return loader_class()
            else:
                raise ValueError(f"Unsupported file format: {suffix}")
        
        raise FileNotFoundError(f"Source not found: {source}")
    
    @classmethod
    def load_document(
        cls,
        source: Union[str, Path],
        config: Optional[Dict] = None
    ) -> str:
        """
        Load document from any supported source
        
        Args:
            source: Path or URL
            config: Configuration
            
        Returns:
            Loaded text
        """
        loader = cls.get_loader(source, config)
        return loader.load(source)
