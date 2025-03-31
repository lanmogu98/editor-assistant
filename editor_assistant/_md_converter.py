#!/usr/bin/env python3
"""
markdown converter

Processes various types of input (files, URLs) and converts them to markdown for further processing.
"""

import json
import logging
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple, Any
from urllib.parse import urlparse
from markitdown import MarkItDown
from ._clean_html_to_md import CleanHTML2Markdown
from ..config.markitdown.support_formats import MARKITDOWN_CONFIG

support_file_suffixes = [formats["extension"] 
                         for file_type in MARKITDOWN_CONFIG["support_formats"] 
                         if file_type != 'url'
                         for formats in MARKITDOWN_CONFIG["support_formats"][file_type]]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class markdownConverter:
    """
    Handles various types of input content and converts them to a standard format.
    """
    
    def __init__(self):
        """
        Initialize the content handler.
        
        Args:
            config_path: Path to the configuration file. If None, will use default.
        """
        self.markitdown = MarkItDown()
        self.clean_html = CleanHTML2Markdown()
    
    def _is_url(self, path: str) -> bool:
        """
        Check if a string is a url.
        """
        parsed_url = urlparse(path)
        return all([parsed_url.scheme in ('http', 'https'), parsed_url.netloc])

    def _is_file(self, path: str) -> bool:
        """
        Check if a string is a path to a file. 
        This is different from checking if it is a url, as a url can be a path to a file.
        
        Args:
            url: The string to check
            
        Returns:
            True if the string is a url or path to a file, False otherwise
        """
        file_suffix = Path(path).suffix.lower()
        return file_suffix in support_file_suffixes

    def _is_html(self, path: str) -> bool:
        """
        Check if a string is a path to a html file.
        """
        suffix = Path(path).suffix.lower()
        is_html_file = suffix == ".html" or suffix == ".htm"
        is_html_page = self._is_url(path) and not self._is_file(path)
        return is_html_file or is_html_page


        
    # check if a input is an html link other than a file path or a url to a file
    # if so, extract the main content instead directly call the converter

    def _get_url_name(self, content_path: str) -> str:
        """
        Get a suitable name for the content.
        
        Args:
            content_path: Path to the content
            
        Returns:
            Name for the content
        """
        if self._is_url(content_path):
            # For URLs, use the domain/path as the name
            parsed_url = urlparse(content_path)
            name = f"{parsed_url.netloc}{parsed_url.path.replace('/', '_')}"
            if name.endswith('_'):
                name = name[:-1]
            # Ensure the name is not too long
            if len(name) > 100:
                name = name[:100]
            return name
        else:
            # For files, use the filename without extension
            return Path(content_path).stem
            
    def get_output_dir(self, content_path: str, model_name: str) -> Path:
        """
        Get the output directory for processing results.
        
        Args:
            content_path: Path to the content
            model_name: Name of the model used for processing
            
        Returns:
            Path to the output directory
        """
        content_name = self.get_content_name(content_path)
        
        if self.is_url(content_path):
            # For URLs, create directory in current working directory
            return Path.cwd() / "llm_summaries" / f"{content_name}_{model_name}"
        else:
            # For files, create directory in the same directory as the file
            return Path(content_path).parent.absolute() / "llm_summaries" / f"{content_name}_{model_name}"
            
    def download_with_cache(self, url: str) -> str:
        """
        Download URL content with caching.
        
        Args:
            url: URL to download
            
        Returns:
            Content of the URL
        """
        import requests
        
        # Create a hash of the URL for the cache filename
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_path = self.cache_dir / f"{url_hash}.json"
        
        # Check if cached version exists and is recent (less than 24 hours old)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cache_time < timedelta(hours=24):
                    logging.info(f"Using cached content for {url}")
                    return cache_data['content']
            except Exception as e:
                logging.warning(f"Error reading cache for {url}: {str(e)}")
        
        # Download the content
        try:
            logging.info(f"Downloading content from {url}")
            response = requests.get(url)
            response.raise_for_status()
            
            # Save to cache
            cache_data = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'content': response.text
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            return response.text
        except Exception as e:
            logging.error(f"Error downloading URL {url}: {str(e)}")
            raise Exception(f"Error downloading URL: {str(e)}") from e
            
    def process_content(self, content_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process content from various sources and convert to a standard format.
        
        Args:
            content_path: Path to a file or URL
            
        Returns:
            Tuple of (processed_content, metadata)
        """
        metadata = {
            "content_path": content_path,
            "content_name": self.get_content_name(content_path),
            "is_url": self.is_url(content_path),
            "original_format": Path(content_path).suffix.lower() if not self.is_url(content_path) else "url",
            "processing_time": 0
        }
        
        start_time = datetime.now()
        
        try:
            # Try to use markitdown if available
            try:
                from markitdown import convert_to_markdown
                logging.info(f"Using markitdown to convert {content_path}")
                
                # Process differently based on whether it's a URL or file
                if self.is_url(content_path):
                    if not self.is_valid_url(content_path):
                        raise ValueError(f"Invalid URL format: {content_path}")
                        
                    # For URLs, pass directly to markitdown
                    processed_content = convert_to_markdown(content_path)
                else:
                    # For files, check if they exist
                    if not os.path.exists(content_path):
                        raise FileNotFoundError(f"File not found: {content_path}")
                        
                    # Convert file to markdown
                    processed_content = convert_to_markdown(content_path)
                    
                metadata["converter"] = "markitdown"
                    
            except ImportError:
                # If markitdown isn't available, use basic approach
                logging.warning("Markitdown library not available. Using basic converter.")
                processed_content = self._basic_converter(content_path)
                metadata["converter"] = "basic"
                
        except Exception as e:
            logging.error(f"Error processing content: {str(e)}")
            raise Exception(f"Error processing content: {str(e)}") from e
            
        # Update metadata
        metadata["processing_time"] = (datetime.now() - start_time).total_seconds()
        
        return processed_content, metadata
        
    def _basic_converter(self, content_path: str) -> str:
        """
        Basic converter for when markitdown is not available.
        
        Args:
            content_path: Path to content
            
        Returns:
            Processed content
        """
        if self.is_url(content_path):
            # Basic URL handling
            return self.download_with_cache(content_path)
            
        # Handle different file types
        ext = Path(content_path).suffix.lower()
        
        if ext == ".pdf":
            try:
                import PyPDF2
                with open(content_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    content = ""
                    for page_num in range(len(pdf_reader.pages)):
                        content += pdf_reader.pages[page_num].extract_text() + "\n\n"
                return content
            except ImportError:
                raise Exception("PDF processing requires PyPDF2 library")
                
        elif ext in (".docx", ".doc"):
            try:
                import docx
                doc = docx.Document(content_path)
                return "\n\n".join([para.text for para in doc.paragraphs])
            except ImportError:
                raise Exception("DOCX processing requires python-docx library")
                
        elif ext == ".html":
            try:
                from bs4 import BeautifulSoup
                with open(content_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                # Extract text and preserve some structure
                return soup.get_text(separator="\n")
            except ImportError:
                # Fallback to basic text reading
                with open(content_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
        else:
            # Default case - try to open as text
            try:
                with open(content_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                # If it's not a text file, raise an error
                raise ValueError(f"Unsupported binary file format: {ext}") 