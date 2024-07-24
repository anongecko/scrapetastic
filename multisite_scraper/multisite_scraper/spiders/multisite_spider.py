import scrapy
import json
from urllib.parse import urlparse
from pathlib import Path
import re
from scrapy.spiders import SitemapSpider
from scrapy_playwright.page import PageMethod
from ..utils.content_extractor import extract_content
from ..utils.data_processor import process_data
from ..utils.link_analyzer import analyze_links
from ..utils.monitoring import log_crawl_status
from ..utils.documentation_generator import generate_documentation

class MultisiteSpider(SitemapSpider):
    name = 'multisite_spider'
    custom_settings = {
        'DEPTH_LIMIT': 5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'DOWNLOAD_DELAY': 1,
        'ROBOTSTXT_OBEY': True,
        'SPIDER_MIDDLEWARES': {
            'scrapy.spidermiddlewares.depth.DepthMiddleware': 100,
            'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 200,
            'multisite_scraper.middlewares.custom_middlewares.IncrementalUpdateMiddleware': 300,
            'multisite_scraper.middlewares.custom_middlewares.ContentDiffMiddleware': 400,
            'multisite_scraper.middlewares.custom_middlewares.AdaptiveCrawlingMiddleware': 500,
        },
        'ITEM_PIPELINES': {
            'multisite_scraper.pipelines.DataValidationPipeline': 100,
            'multisite_scraper.pipelines.DuplicateFilterPipeline': 200,
            'multisite_scraper.pipelines.ExportPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_playwright.middleware.PlaywrightMiddleware': 1000,
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.PlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.PlaywrightDownloadHandler",
        },
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'CONCURRENT_REQUESTS': 16,
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'timeout': 20 * 1000,  # 20 seconds
        },
        'FEEDS': {
            'output/data.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'indent': 4,
            },
            'output/data.csv': {
                'format': 'csv',
                'encoding': 'utf8',
            },
            'output/data.xml': {
                'format': 'xml',
                'encoding': 'utf8',
                'indent': 4,
            },
        },
    }

    def __init__(self, *args, **kwargs):
        super(MultisiteSpider, self).__init__(*args, **kwargs)
        self.start_urls = kwargs.get('start_urls', '').split(',')
        self.allowed_domains = [urlparse(url).netloc for url in self.start_urls]
        self.sitemap_urls = [f"{url}/sitemap.xml" for url in self.start_urls]
        self.max_pages = int(kwargs.get('max_pages', 1000))
        self.page_count = 0
        self.custom_rules = kwargs.get('custom_rules', {})

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "body"),
                ],
            })

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        self.page_count += 1
        if self.page_count > self.max_pages:
            return

        content = extract_content(response, self.custom_rules)
        processed_data = process_data(content, response.url)

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
            json.dump(processed_data, f, ensure_ascii=False, indent=2)

        self.log(f'Saved file {filepath}')

        # Analyze links
        link_analysis = analyze_links(response)

        # Log crawl status
        log_crawl_status(self.page_count, self.max_pages)

        yield processed_data

        # Follow links within the same domain
        for href in response.css('a::attr(href)').getall():
            url = response.urljoin(href)
            if urlparse(url).netloc in self.allowed_domains:
                yield scrapy.Request(url, callback=self.parse, meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "body"),
                    ],
                })

    def closed(self, reason):
        self.log(f"Crawled {self.page_count} pages")
        generate_documentation(self)