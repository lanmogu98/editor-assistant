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

Converted output:
An MDArticle consists of the markdown content as well as necessary metadata.

"""

from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import urllib.request
import urllib.error
from .data_models import MDArticle, InputType
from .config.markitdown_formats import SUPPORTED_FORMATS
from .config.logging_config import error, warning
import logging

LOGGING_LEVEL = logging.INFO

markitdown_supported_formats = SUPPORTED_FORMATS["file_extentions"]

# Logging will be configured by main application

class MarkdownConverter:
    """Handles various types of input and converts them to markdown."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(LOGGING_LEVEL)

    """
    Check if a string is a url.
    """
    def _is_url(self, path: str) -> bool:

        parsed_url = urlparse(path)
        return all([parsed_url.scheme in ('http', 'https'), parsed_url.netloc])


    def _is_url_html(self, url: str) -> bool:
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
                        self.logger.warning (f"URL '{url}' has Content-Type: {content_type} (not HTML)")
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
  
    def convert_content(self, content_path: str, type: InputType = InputType.PAPER) -> Optional[MDArticle]:
        """
        Process content from various sources and convert to a standard format.
        
        Args:
            content_path: Path to a file or URL
            
        Returns:
            Tuple of (processed_content, metadata)
        """

        # initialize the processed content
        md_article= None

            
        # try to convert htmls with html_converter
        if (self._is_url_html(content_path) or self._is_html_file(content_path)):
            self.logger.debug (f"Converting html with html_converter: {content_path}")
            try:
                # clean_html.convert returns a dictionary, default to use readability
                from .clean_html_to_md import CleanHTML2Markdown
                md_article = CleanHTML2Markdown().convert(content_path)
                if md_article is None:
                    self.logger.debug (
                        "Failed to convert with CleanHTML2Markdown:" 
                        f"{content_path}"
                    )
                      
            except Exception as e:
                self.logger.debug (
                    "Failed to convert with CleanHTML2Markdown:"
                    f"{str(e)} - {content_path}"
                )
        
        # if it's not html, or if html conversion fails, try to convert MarkItDown
        if md_article is None:
            try:
                from markitdown import MarkItDown
            except Exception as e:  
                error("markitdown is not installed.")   
            
            try:
                ms_conversion = MarkItDown().convert(content_path)
                md_article = MDArticle(
                    type = type,
                    content = ms_conversion.markdown,
                    title = ms_conversion.title,
                    converter = "MarkItDown",
                    source_path = content_path
                )    
            except Exception as e:
                error (f"Failed to convert input with MarkItDown: {str(e)}")    
                return None
        
        if "https:" in content_path:
            output_dir = Path(content_path.replace("https:", "webpage")).parent
        else:
            output_dir = Path(content_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # format the title
        if (md_article.title is not None) and ("/" in md_article.title):
            md_article.title = md_article.title.replace("/", "-")

        # save the content and insert output path
        md_article.output_path = output_dir / f"{md_article.title}.md"
        with open(md_article.output_path, "w") as f:
            f.write(md_article.title) if md_article.title else None
            f.write(f"\nsource: {md_article.source_path}\n\n")
            f.write(md_article.content)

        return md_article
        
  
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
                    f.write(processed_content.content)
            print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()