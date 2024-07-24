# Scrapetastic

## Description

Scrapetastic is a powerful, flexible, and feature-rich web scraping tool built with Scrapy and enhanced with Playwright for JavaScript rendering. It's designed to efficiently crawl and extract data from multiple websites while adhering to ethical scraping practices. Make sure to create a sites_to_scrape.txt file in your project directory with a list of URLs to scrape, one per line.

## Features

- Multi-domain scraping
- JavaScript rendering support using Playwright
- Configurable depth limit and maximum pages
- Sitemap support for efficient crawling
- Rate limiting and polite crawling practices
- Data deduplication
- Custom extraction rules
- Multiple export formats (JSON, CSV, XML)
- Content analysis and link structure mapping
- Incremental updates
- Adaptive crawling
- Distributed crawling capability
- Built-in monitoring and logging
- Automatic documentation generation

## Requirements

- Python 3.7+
- Scrapy
- Playwright
- Additional dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/anongecko/multisite-web-scraper.git
   cd multisite-web-scraper
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Install Playwright browsers:
   ```
   playwright install
   ```

## Usage

To run the scraper, use the following command:

```
scrapy crawl multisite_spider -a start_urls="https://example.com,https://another-example.com" -a max_pages=100
```

Parameters:
- `start_urls`: Comma-separated list of URLs to start scraping from
- `max_pages`: Maximum number of pages to scrape (default is 1000)

## Configuration

You can customize the scraper's behavior by modifying the following files:
- `multisite_scraper/spiders/multisite_spider.py`: Main spider logic
- `multisite_scraper/settings.py`: Scrapy settings
- `multisite_scraper/middlewares/custom_middlewares.py`: Custom middleware for incremental updates, content diff, and adaptive crawling

## Output

The scraper generates several output files:

1. Individual page data:
   - Location: `data/` directory
   - Format: `{page_name}_{domain}.json`

2. Aggregated data:
   - Location: `output/` directory
   - Formats: 
     - `data.json`: All scraped data in JSON format
     - `data.csv`: All scraped data in CSV format
     - `data.xml`: All scraped data in XML format

3. Documentation:
   - Location: `output/documentation.md`
   - Contains information about the scraper's configuration and data structure

## Customization

### Custom Extraction Rules

You can define custom extraction rules for specific websites by passing a JSON string to the spider:

```
scrapy crawl multisite_spider -a start_urls="https://example.com" -a custom_rules='{"example.com": {"title": "h1::text", "content": "div.main-content p::text"}}'
```

### Extending the Spider

To add new features or modify existing ones, edit the `MultisiteSpider` class in `multisite_scraper/spiders/multisite_spider.py`.

## Ethical Considerations

This scraper is designed with ethical web scraping practices in mind. It respects `robots.txt` files, implements rate limiting, and avoids overloading servers. Always ensure you have permission to scrape a website and comply with its terms of service.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and research purposes only. Always respect website terms of service and use responsibly.
