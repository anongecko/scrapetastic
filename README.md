# Scrapetastic

## Description

Scrapetastic is a powerful, flexible, and feature-rich web scraping tool built with Scrapy and enhanced with Playwright for JavaScript rendering. It's designed to efficiently crawl and extract data from multiple websites while adhering to ethical scraping practices. This scraper can handle modern web applications, including those with dynamic content and toggle-able sections.

## Features

- Multi-domain scraping from a user-defined list
- JavaScript rendering support using Playwright
- Handling of toggle-able and dynamically loaded content
- Configurable depth limit and maximum pages per site
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
- Progress tracking for each website
- Automatic updating of the sites-to-scrape list

## Requirements

- Python 3.7+
- Scrapy
- Playwright
- tqdm (for progress bars)
- Additional dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/multisite-web-scraper.git
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

1. Create a file named `sites_to_scrape.txt` in the project root directory. Add the URLs of the websites you want to scrape, one per line.

2. Run the scraper using the following command:
   ```
   scrapy crawl multisite_spider -a sites_file=sites_to_scrape.txt -a max_pages=100
   ```

   Parameters:
   - `sites_file`: Path to the file containing the list of URLs to scrape (default is 'sites_to_scrape.txt')
   - `max_pages`: Maximum number of pages to scrape per website (default is 1000)

3. The scraper will display progress bars for each website being crawled. Once a site is fully crawled or reaches the max_pages limit, it will be removed from the sites_to_scrape.txt file.

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

4. Crawl Report:
   - Location: `output/crawl_report.json`
   - Contains statistics about the crawl, including duration, pages crawled, and sites processed

## Customization

### Custom Extraction Rules

You can define custom extraction rules for specific websites by passing a JSON string to the spider:

```
scrapy crawl multisite_spider -a sites_file=sites_to_scrape.txt -a max_pages=100 -a custom_rules='{"example.com": {"title": "h1::text", "content": "div.main-content p::text"}}'
```

### Extending the Spider

To add new features or modify existing ones, edit the `MultisiteSpider` class in `multisite_scraper/spiders/multisite_spider.py`.

## Handling Toggle-able Content

The scraper attempts to reveal hidden content by interacting with common toggle elements. You can customize the selectors used for this in the `toggle_selectors` list within the `MultisiteSpider` class.

## Ethical Considerations

This scraper is designed with ethical web scraping practices in mind. It respects `robots.txt` files, implements rate limiting, and avoids overloading servers. Always ensure you have permission to scrape a website and comply with its terms of service.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and research purposes only. Always respect website terms of service and use responsibly.
```

This README provides a comprehensive overview of your Multisite Web Scraper project, including its features, installation instructions, usage guidelines, output description, customization options, and ethical considerations. It also highlights the new features such as reading sites from a file, progress tracking, and automatic updating of the sites list.

Remember to replace `yourusername` in the git clone URL with your actual GitHub username or organization name. Also, if you haven't already, consider adding a LICENSE file to your repository to clarify the terms under which your project can be used and distributed.
