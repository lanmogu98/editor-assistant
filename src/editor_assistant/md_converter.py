#!/usr/bin/env python3
"""
markdown converter

Processes various types of input (files, URLs) and converts them to markdown 
for further processing.

Two converters are employed:
1. CleanHTML2Markdown: named html_converter, for html urls and html files
2. MarkItDown: named ms_converter, for other input types

Workflow is as follows:
1. Check if the input is a html url path or a html file path
2. if so, html_converter is used to convert the input to markdown
3. Else, other input types are converted by ms_converter

"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import urllib.request
import urllib.error
from .data_models import MDArticle

from .clean_html_to_md import CleanHTML2Markdown
from .config.markitdown_formats import SUPPORTED_FORMATS

markitdown_supported_formats = SUPPORTED_FORMATS["file_extentions"]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MarkdownConverter:
    """
    Handles various types of input and converts them to markdown.
    """
    
    def __init__(self):
        """
        Initialize the content handler.
        
        Args:
            config_path: Path to the configuration file. If None, will use default.
        """
        # use microsoft markitdown converter to handle requests other 
        # than html page or file, in case html needs pre-formatting 
        # before being converted to markdown
        try:
            from markitdown import MarkItDown
        except ImportError: 
            raise ImportError("MarkItDown is not installed")
    
        self.ms_converter = MarkItDown()
        self.html_converter = CleanHTML2Markdown()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Markdown Converter Initialized")

    """
    Check if a string is a url.
    """
    def _is_url(self, path: str) -> bool:

        parsed_url = urlparse(path)
        return all([parsed_url.scheme in ('http', 'https'), parsed_url.netloc])


    def _is_html_url(self, url: str) -> bool:
        """
        Args:
            url: The URL string to check.

        Returns:
            True if the URL is valid and the Content-Type indicates HTML, 
            False otherwise.
        """
        if not self._is_url(url):
            return False

        try:
            # Create a request object explicitly setting the method to HEAD. 
            # This is to avoid downloading the entire page.
            req = urllib.request.Request(url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0')

            with urllib.request.urlopen(req, timeout=10) as response: 
                # Check the status code (optional, but good practice)
                if response.getcode () == 200:
                    content_type = response.headers.get ('Content-Type')
                    if content_type and (content_type.strip().lower().
                       startswith ('text/html') or 
                       content_type.strip().lower().
                       startswith ('application/xhtml+xml')):
                        return True
                    else:
                        print (f"URL '{url}' has Content-Type:\
                              {content_type} (not HTML)")
                        return False
                else:
                    raise Exception (f"Error accessing URL '{url}': {response.getcode()}")


        except urllib.error.URLError as e:
            raise Exception(f"Error accessing URL '{url}': {e.reason}")

    """
    Check if a string is a path to a html file.
    """
    def _is_html_file (self, path: str) -> bool:
        suffix = Path(path).suffix.lower()
        return suffix == ".html" or suffix == ".htm"
    
    """
    Check if a string is a path to a supported file.
    """
    def _is_supported_file (self, path: str) -> bool:
        """
        Args:
            path: The string to check
            
        Returns:
            True if the string is a url or path to a file, False otherwise
        """
        is_supported_file = Path(path).suffix.lower() in markitdown_supported_formats
        return is_supported_file

    """
    Get a suitable name for the content.
    """
    def _get_input_name (self, content_path: str) -> str:
        """
        Args:
            content_path: Path to the content
            
        Returns:
            Name for the content
        """
        
        # for urls, use the domain/path as the name
        if self._is_url(content_path):
            parsed_url = urlparse(content_path)
            name = f"{parsed_url.netloc}{parsed_url.path.replace('/', '_')}"
            if name.endswith('_'):
                name = name[:-1]
            # Ensure the name is not too long
            if len(name) > 100:
                name = name[:100]
            return name
        # other types of input
        else: 
            return Path(content_path).stem

    def get_output_dir (self, content_path: str, model_name: str) -> Path:
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
            
  
    def convert_content(self, content_path: str) -> Optional[MDArticle]:
        """
        Process content from various sources and convert to a standard format.
        
        Args:
            content_path: Path to a file or URL
            
        Returns:
            Tuple of (processed_content, metadata)
        """

        # check if the content is supported
        if (not self._is_supported_file(content_path) and 
            not self._is_html_url(content_path) and 
            not self._is_html_file(content_path)):
            self.logger.warning (f"Unknown content type, conversion might fail: {content_path}")

        # initialize the processed content
        processed_content = None

        # # try to convert htmls with html_converter
        # if (self._is_html_url(content_path) or self._is_html_file(content_path)):
        #     self.logger.debug (f"Converting html with html_converter: {content_path}")
        #     try:
        #         # clean_html.convert returns a dictionary
        #         processed_content = self.html_converter.convert(content_path, 
        #                                                             "readabilipy")
        #         if processed_content is None:
        #             self.logger.warning (
        #                 "Failed to convert with CleanHTML2Markdown:" 
        #                 f"{content_path}"
        #             )
        #         else:
        #             success = True
                    
        #     except Exception as e:
        #         self.logger.warning (
        #             "Failed to convert with CleanHTML2Markdown:"
        #             f"{str(e)} - {content_path}"
        #         )
        
        # if it's not html, or if html conversion fails, try to convert with ms_converter
        if processed_content is None:
            try:
                md_content = self.ms_converter.convert(content_path).text_content
                processed_content = MDArticle(
                    markdown_content=md_content,
                    title=self._get_input_name(content_path),
                    authors=None,
                    source_path=content_path,
                    converter="MarkItDown"
                )
            except Exception as e:
                self.logger.warning (f"Failed to convert input with MarkItDown: {str(e)}")
        
        return processed_content
        
  
def test_md_converter():
    """
    Test the md_converter class.
    """
    import pandas as pd
    converter = MarkdownConverter()
    print(f"{'='*50}")
    print(">> converter initialized.\n")
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    export_path = Path("./samples") / "test_results" / f"{now}"
    export_path.mkdir(parents=True, exist_ok=True)

    test_file = "./samples/test_cases.xlsx"
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
        client, url= row['client'], row['paper_url']
                                        
        if isinstance(url, str):
            try:
                processed_content, metadata = \
                                    converter.convert_content (url)
                with open(export_path / f"url_{client}_{metadata['title']}.md", "w") as f:
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

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Convert markdown to markdown.")
    parser.add_argument("content_paths", 
                        nargs= '+', 
                        help= "Path(s) to the research paper markdown file(s)")
    parser.add_argument("-o", "--output", 
                        help= "Path to the output directory")
    args = parser.parse_args()
    converter = MarkdownConverter()
    for content_path in args.content_paths:
        processed_content = converter.convert_content(content_path)
        if processed_content is None:
            print(f"Failed to convert {content_path}")
            continue
        else:
            print(f"Successfully converted {content_path}")
            if args.output:
                output_path = Path(args.output) / f"{processed_content.title}.md"
            else:
                output_path = Path.cwd() / "md" / f"{processed_content.title}.md"
            
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w") as f:
                    f.write(f"url: {processed_content.source_path}\n\n")
                    f.write(f"title: {processed_content.title}\n\n")
                    f.write(f"authors: {processed_content.authors}\n\n")
                    f.write(processed_content.markdown_content)
            print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()