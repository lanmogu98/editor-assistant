#!/usr/bin/env python3
"""
markdown converter

Processes various types of input (files, URLs) and converts them to markdown 
for further processing.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Any
from urllib.parse import urlparse
import urllib.request
import urllib.error

from ._clean_html_to_md import CleanHTML2Markdown

from ..config.markitdown.support_formats import SUPPORTED_FORMATS
support_file_suffixes = SUPPORTED_FORMATS["file_extentions"]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class markdownConverter:
    """
    Handles various types of input and converts them to markdown.
    """
    
    def __init__(self):
        """
        Initialize the content handler.
        
        Args:
            config_path: Path to the configuration file. If None, will use default.
        """
        try:
            from markitdown import MarkItDown
            self.markitdown = MarkItDown()
        except ImportError: 
            self.markitdown = None
        self.clean_html = CleanHTML2Markdown()
    
    """
    Check if a string is a url.
    """
    def _is_url(self, path: str) -> bool:

        parsed_url = urlparse(path)
        return all([parsed_url.scheme in ('http', 'https'), parsed_url.netloc])

    def _get_url_type(self, url: str) -> str:
        """
        Checks if a URL points to an HTML page by checking the Content-Type 
        header.
        """
        assert self._is_url(url)

        try:
             # Create a request object explicitly setting the method to HEAD. 
            # This is to avoid downloading the entire page.
            req = urllib.request.Request(url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0')


            with urllib.request.urlopen(req, timeout=10) as response: 
                # Check the status code (optional, but good practice)
                if response.getcode() == 200:
                    content_type = response.headers.get('Content-Type')
                    if content_type and (content_type.strip().lower().
                       startswith('text/html') or 
                       content_type.strip().lower().
                       startswith('application/xhtml+xml')):
                        return "html"
                    else:
                        print(f"URL '{url}' has Content-Type:\
                              {content_type} (not HTML)")
                        return False
                else:
                    print(f"URL '{url}' returned status code: \
                          {response.getcode()}")
                    return False
        except urllib.error.URLError as e:
            print(f"Error accessing URL '{url}': {e.reason}")
            return False
        except Exception as e:
            # Catch other potential errors like timeouts
            print(f"An unexpected error occurred for URL '{url}': {e}")
            return False
    def _is_html_url(self, url: str) -> bool:
        """
        Args:
            url: The URL string to check.

        Returns:
            True if the URL is valid and the Content-Type indicates HTML, 
            False otherwise.
        """
        assert self._is_url(url)

        try:
            # Create a request object explicitly setting the method to HEAD. 
            # This is to avoid downloading the entire page.
            req = urllib.request.Request(url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0')


            with urllib.request.urlopen(req, timeout=10) as response: 
                # Check the status code (optional, but good practice)
                if response.getcode() == 200:
                    content_type = response.headers.get('Content-Type')
                    if content_type and (content_type.strip().lower().
                       startswith('text/html') or 
                       content_type.strip().lower().
                       startswith('application/xhtml+xml')):
                        return True
                    else:
                        print(f"URL '{url}' has Content-Type:\
                              {content_type} (not HTML)")
                        return False
                else:
                    print(f"URL '{url}' returned status code: \
                          {response.getcode()}")
                    return False
        except urllib.error.URLError as e:
            print(f"Error accessing URL '{url}': {e.reason}")
            return False
        except Exception as e:
            # Catch other potential errors like timeouts
            print(f"An unexpected error occurred for URL '{url}': {e}")
            return False

    """
    Check if a string is a path to a supported file.
    """
    def _is_supported_file(self, path: str) -> bool:
        """
        Args:
            path: The string to check
            
        Returns:
            True if the string is a url or path to a file, False otherwise
        """
        file_suffix = Path(path).suffix.lower()
        if self._is_url(path):
            r
        return file_suffix in support_file_suffixes

    def _is_html(self, path: str) -> bool:
        """
        Check if a string is a path to a html file.
        """
        suffix = Path(path).suffix.lower()
        is_html_file = suffix == ".html" or suffix == ".htm"
        is_html_page = self._is_html_url(path)
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

        assert (self._is_html_url(content_path) or 
                self._is_supported_file(content_path))
        
        # for html urls, use the domain/path as the name
        if self._is_html_url(content_path):
            parsed_url = urlparse(content_path)
            name = f"{parsed_url.netloc}{parsed_url.path.replace('/', '_')}"
            if name.endswith('_'):
                name = name[:-1]
            # Ensure the name is not too long
            if len(name) > 100:
                name = name[:100]
            return name
        else:  # for supported files, use the filename without extension
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
        
        if self._is_url(content_path):
            # For URLs, create directory in current working directory
            return Path.cwd() / "llm_summaries" / f"{content_name}_{model_name}"
        else:
            # For files, create directory in the same directory as the file
            return (Path(content_path).parent.absolute() / "llm_summaries" / 
                    f"{content_name}_{model_name}")
            
  
    def process_content(self, content_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process content from various sources and convert to a standard format.
        
        Args:
            content_path: Path to a file or URL
            
        Returns:
            Tuple of (processed_content, metadata)
        """

        # check if the content is supported
        if (not self._is_supported_file(content_path) and 
            not self._is_html(content_path)):
            raise ValueError(f"Unsupported content type: {content_path}")

        metadata = {
            "content_path": content_path,
            "content_name": None,
            "converter": None,
            "processing_time": 0
        }
        
        start_time = datetime.now()
        
        if self._is_html(content_path):
            try:
                # clean_html.convert returns a dictionary
                processed_content_dict = self.clean_html.convert(content_path, "readabilipy")
                processed_content = processed_content_dict['markdown'] # Extract markdown string
                metadata["converter"] = "CleanHTML2Markdown"
                # Optionally add other details to metadata
                metadata["title"] = processed_content_dict.get('title')
                metadata["authors"] = processed_content_dict.get('authors')
            except Exception as e:
                raise Exception(f"Error coverting with CleanHTML2Markdown: {str(e)}") from e
        else:
            try:
                processed_content = self.markitdown.convert(content_path).text_content
                metadata["converter"] = "MarkItDown"
            except Exception as e:
                raise Exception(f"Error coverting with MarkItDown: {str(e)}") from e
        
        # Update metadata
        if self._is_url(content_path):
            metadata["content_name"] = self._get_url_name(content_path)
        else:
            metadata["content_name"] = Path(content_path).stem.replace("/", "_")
        
        metadata["processing_time"] = (datetime.now() - start_time).total_seconds()
        
        return processed_content, metadata
        
  
def test_md_converter():
    """
    Test the md_converter class.
    """
    import pandas as pd
    converter = markdownConverter()
    print(f"{'='*50}")
    print(">> converter initialized.\n")
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    export_path = Path("./samples") / "client_tests" / f"{now}"
    export_path.mkdir(parents=True, exist_ok=True)

    test_file = "./samples/client_test_cases.xlsx"
    df = pd.read_excel(test_file)

    results = {
            "url":{
                "success_count":0,
                "failed_count":0,
                "success":[],
                "failed":[]
            }, 
            "html":{
                "success_count":0,
                "failed_count":0,
                "success":[],
                "failed":[]
            }, 
            "pdf":{
                "success_count":0,
                "failed_count":0,
                "success":[],
                "failed":[]
            }
    }  

    for _, row in df.iterrows():
        processed_content, metadata = None, None
        client, url, html_path,pdf_path = row['client'], row['paper_url'], \
                                        row['html_path'],row['pdf_path']
        if isinstance(url, str):
            try:
                processed_content, metadata = \
                                    converter.process_content(url)
                with open(export_path / f"url_{client}_{metadata['content_name']}.md", "w") as f:
                    f.write(processed_content)
                print(f">> Success on URL of {client}" )
                print(metadata)
                print(f"{'-'*50}")
                results["url"]["success_count"] += 1
                results["url"]["success"].append(client)
            except Exception as e:
                print(f">> Failed on URL of {client}")
                logging.error(f"Error processing url: {url} - {str(e)}")
                print(f"{'-'*50}")
                results["url"]["failed_count"] += 1
                results["url"]["failed"].append(client)
        """   
        if isinstance(html_path, str):
            try:
                processed_content, metadata = \
                converter.process_content(html_path, export_path / f"html_{client}.md")
            except Exception as e:
                logging.error(f"Error processing html: {html_path} - {str(e)}")
                raise Exception(f"Error processing html: {html_path} - {str(e)}") from e
        """ 
    
    print(f"\n{'='*50}")
    print(results)
if __name__ == "__main__":
    test_md_converter()