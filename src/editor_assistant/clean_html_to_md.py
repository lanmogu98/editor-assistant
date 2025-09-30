#!/usr/bin/env python3
"""
This module is used to convert html to clean markdown, 
extracting only the main content from a webpage
and removing all the noise like ads, headers, footers, etc.
"""

import requests
import time
from .data_models import MDArticle, InputType
import logging
from typing import Optional
from enum import Enum
import json

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

class Converter(Enum):
    READABILIPY = "readabilipy"
    TRAFILATURA = "trafilatura"

# class to convert html to markdown
class CleanHTML2Markdown:
    def __init__(self):
        self.h2t = self._init_html2text()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    # initialize html2text
    def _init_html2text(self):
        import html2text
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.body_width = 0
        return self.h2t

    # Fetch the html content from the path
    def _fetch_html_content(self, path) -> str:
        # handle url
        if path.startswith("http"):
            try:
                response = requests.get(path, headers=HEADERS)
                response.raise_for_status()
                return response.text
            except Exception as e:
                self.logger.error(
                    f"Error fetching html content from {path}: "
                    f"{str(e)}"
                )
                return None
        else:
            # handle local file
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                self.logger.error(
                    f"Error fetching html content from {path}: "
                    f"{str(e)}"
                )
                return None

    # convert html to markdown using readabilipy
    def _convert_by_readabilipy(self, path) -> MDArticle:
        try:
            from readabilipy import simple_json_from_html_string
        except ImportError:
            raise ImportError(
                "readabilipy is not installed."
                "Please install it with 'pip install readabilipy'."
            )
        
        # fetch html content
        content = self._fetch_html_content(path)
        if not content:
            self.logger.error(f"Error fetching html content from {path}")
            return None

        # Use Readability to extract the main content
        article = simple_json_from_html_string(content, use_readability=True)
    
        # Initialize html2text
        h2t = self._init_html2text()
        
        # Convert HTML to Markdown
        markdown_content = h2t.handle(article['content'])

        return MDArticle(
            type=InputType.PAPER,
            content=markdown_content,
            title=article['title'],
            authors=article['byline'],
            source_path=path,
            converter="readabilipy",
        )

    # convert html to markdown using trafilatura
    def _convert_by_trafilatura(self, path) -> Optional[MDArticle]:
        try:
            import trafilatura
        except ImportError:
            raise ImportError(
                "trafilatura is not installed."
                "Please install it with 'pip install trafilatura'."
            )

        # fetch html content
        html_content = self._fetch_html_content(path)
        if not html_content:
            self.logger.error(f"trafilatura failed to fetch content from {path}")
            return None

        # extract the main content
        markdown_content = trafilatura.extract(
            html_content, 
            output_format='markdown',
            include_images=True,
            include_tables=True,
            include_links=True,
            include_comments=False
        )
        if not markdown_content:
            self.logger.error(f"trafilatura failed to extract content from {path}")
            return None

        # extract metadata
        metadata_json = trafilatura.extract(
                html_content, 
                with_metadata=True,
                output_format='json',
                include_comments=False
            )
        
        metadata = json.loads(metadata_json) if metadata_json else None
        title = metadata.get('title', '') if metadata else ''
        authors = metadata.get('authors', '') if metadata else ''
        
        return MDArticle(
            type=InputType.PAPER,
            content=markdown_content,
            title=title,
            authors=authors,
            source_path=path,
            converter="trafilatura",
        )

    def convert(self, path, converter_name = Converter.READABILIPY.value) -> Optional[MDArticle]:
        match converter_name:
            case Converter.READABILIPY.value:
                return self._convert_by_readabilipy(path)
            case Converter.TRAFILATURA.value:
                return self._convert_by_trafilatura(path)
            case _:
                raise ValueError(f"Invalid converter name: {converter_name}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Convert an HTML page to clean markdown.")
    parser.add_argument("path", help="URL or local file path of the HTML to convert.")
    parser.add_argument("-o", "--output", help="Path to save the output markdown file.")
    parser.add_argument(
        "--converter",
        choices=[Converter.TRAFILATURA, Converter.READABILIPY],
        default=Converter.TRAFILATURA,
        help="The converter library to use."
    )
    args = parser.parse_args()

    converter = CleanHTML2Markdown()
    
    print(f"Converting {args.path} using {args.converter}...")
    result = converter.convert(args.path, converter_name=args.converter)

    if result:
        print(f"Successfully converted '{result.title}'.")
        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(result.content)
                print(f"Saved markdown to {args.output}")
            except Exception as e:
                print(f"Error saving to file: {e}")
        else:
            # Print to console if no output file is specified
            print("\n--- Markdown Content ---\n")
            print(result.content)
    else:
        print(f"Failed to convert {args.path}")

"""
test helper functions
"""
def test_converter(url, export_path, converter_name):
    converter = CleanHTML2Markdown()
    result = converter.convert(url, converter_name)
    if result:
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(f"title: {result.title}\n")
            f.write(f"url: {result.source_path}\n")
            f.write(f"authors: {result.authors}\n")
            f.write(result.content)
    

def direct_markitdown(url: str) :
    from markitdown import MarkItDown
    converter = MarkItDown()
    return converter.convert(url).text_content




if __name__ == "__main__":
    nature_no_paywall_url = "https://www.nature.com/articles/d41586-025-01852-z"
    nature_paywall_url = "https://www.nature.com/articles/d41586-025-00704-0"
    ars_url = "https://arstechnica.com/science/2025/03/how-whale-urine-benefits-the-ocean-ecosystem/"

    #test_converter(nature_no_paywall_url, "./samples/nature_no_paywall_readabilipy.md", Converter.READABILIPY)
    test_converter(nature_no_paywall_url, "./samples/nature_no_paywall_trafilatura.md", Converter.TRAFILATURA)
    """
    import pandas as pd
    from pathlib import Path
    client_article_samples_path = "./samples/client_test_cases.xlsx"
    df = pd.read_excel(client_article_samples_path)
    export_path = Path("./samples") / "client_tests"
    export_path.mkdir(parents=True, exist_ok=True)
    
    for _, row in df.iterrows():
        client, url, html_path = row['client'], row['paper_url'], row['html_path']
        if isinstance(url, str):
            test_readabilipy(url, export_path / f"url_{client}.md")
        if isinstance(html_path, str):
            test_readabilipy(html_path, export_path / f"html_{client}.md")
    print(f"{'='*50}")
    """
    """
    print(">> extract_with_readability\n")
    result2= extract_with_readability(url)
    if result2:
        print(f"time: {result2['time']}")
        print(result2['title'])
        print(result2['url'])
        print(result2['markdown'])

    print(f"{'='*50}")
    
    print(">> extract_with_trafilatura\n")
    result3= extract_with_trafilatura(url)
    if result3:
        print(result3['markdown'])
    print(f"{'='*50}")
    print(">> extract_with_goose3\n")
    result4= extract_with_goose3(url)
    if result4:
        print(result4['markdown'])
    print(f"{'='*50}")
    
    print(">> extract_with_readabilipy\n")
    result5 = extract_with_readabilipy(url)
    if result5:
        print(f"time: {result5['time']}\n")
        print(f"title: {result5['title']}\n")
        print(f"byline: {result5['byline']}\n")
        print(f"url: {result5['url']}\n")
        print(f"markdown:\n {result5['markdown']}\n")
"""