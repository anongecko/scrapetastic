import scrapy
from scrapy.spiders import SitemapSpider
from scrapy_playwright.page import PageMethod
from urllib.parse import urlparse
from pathlib import Path
import re
import json
import asyncio
import hashlib
from datetime import datetime
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
                'item_export_kwargs': {
                    'export_empty_fields': False,
                },
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
        'HTTPCACHE_ENABLED': True,
        'HTTPCACHE_EXPIRATION_SECS': 0,  # Never expire
        'HTTPCACHE_DIR': 'httpcache',
        'HTTPCACHE_IGNORE_HTTP_CODES': [],
        'HTTPCACHE_STORAGE': 'scrapy.extensions.httpcache.FilesystemCacheStorage',
    }

    def __init__(self, *args, **kwargs):
        super(MultisiteSpider, self).__init__(*args, **kwargs)
        self.start_urls = kwargs.get('start_urls', '').split(',')
        self.allowed_domains = [urlparse(url).netloc for url in self.start_urls]
        self.sitemap_urls = [f"{url}/sitemap.xml" for url in self.start_urls]
        self.max_pages = int(kwargs.get('max_pages', 1000))
        self.page_count = 0
        self.custom_rules = json.loads(kwargs.get('custom_rules', '{}'))
        self.start_time = datetime.now()
        self.toggle_selectors = [
            ".code-tab",
            "[data-toggle='code']",
            ".toggle-code-button",
            ".tab-button",
            ".accordion-header",
            "[role='tab']",
            # Add more selectors as needed
        ]

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

        try:
            # Identify and interact with toggle-able sections
            await self.reveal_hidden_content(page)

            # Get the updated HTML content after revealing hidden sections
            content = await page.content()

            # Create a new response object with the updated content
            new_response = response.replace(body=content)

            self.page_count += 1
            if self.page_count > self.max_pages:
                await page.close()
                return

            extracted_content = extract_content(new_response, self.custom_rules.get(urlparse(response.url).netloc, {}))
            processed_data = process_data(extracted_content, response.url)

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
            link_analysis = analyze_links(new_response)
            processed_data['link_analysis'] = link_analysis

            # Log crawl status
            log_crawl_status(self.page_count, self.max_pages)

            yield processed_data

            # Follow links within the same domain
            for href in new_response.css('a::attr(href)').getall():
                url = response.urljoin(href)
                if urlparse(url).netloc in self.allowed_domains:
                    yield scrapy.Request(url, callback=self.parse, meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "body"),
                        ],
                    })

        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {str(e)}")
        finally:
            await page.close()

    async def reveal_hidden_content(self, page):
        for selector in self.toggle_selectors:
            toggles = await page.query_selector_all(selector)
            for toggle in toggles:
                try:
                    await toggle.click()
                    # Wait a bit for any animations to complete
                    await asyncio.sleep(0.5)
                except Exception as e:
                    self.logger.warning(f"Failed to click toggle {selector}: {str(e)}")

        # Scroll the page to trigger lazy-loaded content
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)  # Wait for any lazy-loaded content to appear

    def closed(self, reason):
        end_time = datetime.now()
        duration = end_time - self.start_time
        self.log(f"Crawl finished. Reason: {reason}")
        self.log(f"Total pages crawled: {self.page_count}")
        self.log(f"Total duration: {duration}")
        generate_documentation(self)

        # Generate a crawl report
        report = {
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration": str(duration),
            "total_pages": self.page_count,
            "max_pages": self.max_pages,
            "allowed_domains": self.allowed_domains,
            "reason": reason
        }
        
        with open('output/crawl_report.json', 'w') as f:
            json.dump(report, f, indent=2)

    def parse_sitemap(self, response):
        """Override SitemapSpider's parse_sitemap method to use Playwright"""
        return scrapy.Request(response.url, callback=self.parse, meta={
            "playwright": True,
            "playwright_include_page": True,
            "playwright_page_methods": [
                PageMethod("wait_for_selector", "body"),
            ],
        })