import scrapy
import json
import os
from urllib.parse import urlparse
from pathlib import Path
import re

class MultisiteSpider(scrapy.Spider):
    name = 'multisite_spider'

    def __init__(self, *args, **kwargs):
        super(MultisiteSpider, self).__init__(*args, **kwargs)
        self.start_urls = kwargs.get('start_urls', '').split(',')
        self.allowed_domains = [urlparse(url).netloc for url in self.start_urls]
        self.max_pages = int(kwargs.get('max_pages', 1000))
        self.page_count = 0

    def parse(self, response):
        self.page_count += 1
        if self.page_count > self.max_pages:
            return

        # Extract content
        content = []
        for element in response.css('body *:not(script):not(style)'):
            if element.root.tag in ['pre', 'code']:
                content.append({
                    'type': 'code',
                    'content': element.get()
                })
            elif element.root.tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']:
                content.append({
                    'type': 'text',
                    'content': element.css('::text').get()
                })

        # Create data
        data = {
            'url': response.url,
            'title': response.css('title::text').get(),
            'content': content
        }

        # Create filename
        parsed_url = urlparse(response.url)
        page_name = parsed_url.path.strip('/').replace('/', '_') or 'index'
        page_name = re.sub(r'[^\w\-_\. ]', '_', page_name)
        filename = f"{page_name}_{parsed_url.netloc}.json"
        filename = filename[:200]  # Limit filename length
        filepath = Path('data') / filename

        # Ensure data directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Save to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.log(f'Saved file {filepath}')

        # Follow links within the same domain
        for href in response.css('a::attr(href)').getall():
            url = response.urljoin(href)
            if urlparse(url).netloc in self.allowed_domains:
                yield scrapy.Request(url, callback=self.parse)

    def close(self, reason):
        self.log(f"Crawled {self.page_count} pages")