#!/usr/bin/env python3
"""
This module is used to convert html to clean markdown, 
extracting only the main content from a webpage
and removing all the noise like ads, headers, footers, etc.
"""

import requests
import time

class CleanHTML2Markdown:
    def __init__(self):
        self.h2t = self._init_html2text()

    def _init_html2text(self):
        import html2text

        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_tables = False
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0  # Don't wrap text
        return self.h2t
    
    def _convert_by_readabilipy(self, path):
        try:
            from readabilipy import simple_json_from_html_string
        except ImportError:
            raise ImportError(
                "readabilipy is not installed. \
                 Please install it with 'pip install readabilipy'.")
        
        if path.startswith("http"):
            try:
                # for url
                response = requests.get(path)
                response.raise_for_status()
                content = response.text
            except Exception as e:
                print(f"Error extracting url with Readabilipy from {path}: \
                      {str(e)}")
                return None
        else:
            # for local file
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"Error extracting local file with Readabilipy from {path}: \
                      {str(e)}")
                return None
    
        # Use Readability to extract the main content
        article = simple_json_from_html_string(content, use_readability=True)
    
        # Initialize html2text
        h2t = self._init_html2text()
        
        # Convert HTML to Markdown
        markdown_content = h2t.handle(article['content'])

        return {
            'title': article['title'],
            'authors': article['byline'],
            'markdown': markdown_content,
            'url': path,
        }

    def convert(self, path, converter_name = "readabilipy"):
        match converter_name:
            case "readabilipy":
                return self._convert_by_readabilipy(path)
            case _:
                raise ValueError(f"Invalid converter name: {converter_name}")


"""
test helper functions
"""
def test_readabilipy(url, export_path):
    time_start = time.time()
    converter = CleanHTML2Markdown()
    result = converter.convert(url)
    time_end = time.time()
    if result:
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(f"time: {time_end - time_start}\n")
            f.write(f"title: {result['title']}\n")
            f.write(f"url: {result['url']}\n")
            f.write(f"authors: {result['authors']}\n")
            f.write(result['markdown'])
    
# TODO: add other methods if needed

def extract_with_goose3(url):
    from goose3 import Goose

    """
    Extract article content using Goose3
    
    Args:
        url (str): URL of the page to extract
        
    Returns:
        dict: Dictionary with title and markdown content
    """
    try:
        # Initialize Goose
        g = Goose()
        
        # Extract article
        article = g.extract(url=url)
        
        # Get title and content
        title = article.title
        content_html = article.cleaned_text
        
        # Initialize html2text if needed for further formatting
        h2t = init_html2text()
        
        # Convert to markdown if needed (Goose already returns cleaned text)
        markdown_content = h2t.handle(content_html)
        
        return {
            'title': title,
            'markdown': markdown_content,
            'url': url
        }
        
    except Exception as e:
        print(f"Error extracting content with Goose3: {str(e)}")
        return None

def extract_with_trafilatura(url):
    import trafilatura

    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        print(f"trafilatura failed to download content from {url}")
        return None
    html_content = trafilatura.extract(
        downloaded, 
        output_format='html',
        include_images=True,
        include_tables=True
    )

    if not html_content:
        print(f"trafilatura failed to extract content from downloaded content from {url}")
        return None

    h2t = init_html2text()
    markdown_content = h2t.handle(html_content)

    title = trafilatura.metadata(downloaded, output_format='python').get('title', '')

    if not title:
        print(f"Warning: No title found for downloaded content from {url}")
        title = url.split('/')[-1]

    return {
        'title': title,
        'markdown': markdown_content,
        'url': url
    }

def extract_with_readability(url):
    from readability import Document

    """
    Extract article content and convert to Markdown
    
    Args:
        url (str): URL of the page to extract
        
    Returns:
        dict: Dictionary with title and markdown content
    """
    time_start = time.time()
    try:
        # Set a user agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # Get the page content
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Use Readability to extract the main content
        doc = Document(response.text)
        title = doc.title()
        content_html = doc.summary()
        
        # Initialize html2text
        h2t = _init_html2text()
        
        # Convert HTML to Markdown
        markdown_content = h2t.handle(content_html)
        time_end = time.time()
        return {
            'title': title,
            'markdown': markdown_content,
            'url': url,
            'time': time_end - time_start
        }
        
    except Exception as e:
        print(f"Error extracting content: {str(e)}")
        return None

def direct_markitdown(url: str) :
    from markitdown import MarkItDown
    converter = MarkItDown()
    return converter.convert(url).text_content


if __name__ == "__main__":
    nature_no_paywall_url = "https://doi.org/10.1038/d41586-025-00509-1"
    nature_paywall_url = "https://www.nature.com/articles/d41586-025-00704-0"
    ars_url = "https://arstechnica.com/science/2025/03/how-whale-urine-benefits-the-ocean-ecosystem/"

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