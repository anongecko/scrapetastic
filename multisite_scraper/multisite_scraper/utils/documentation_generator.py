def generate_documentation(spider):
    """
    Generate documentation about the scraped data structure.
    """
    doc = f"# {spider.name} Documentation\n\n"
    doc += f"This spider crawls the following domains: {', '.join(spider.allowed_domains)}\n\n"
    doc += f"Maximum pages to crawl: {spider.max_pages}\n\n"
    doc += "## Data Structure\n\n"
    doc += "Each scraped item contains the following fields:\n\n"
    doc += "- url: The URL of the scraped page\n"
    doc += "- content: The extracted content of the page\n"
    doc += "- content_hash: A hash of the content for deduplication purposes\n"

    with open('output/documentation.md', 'w') as f:
        f.write(doc)

    spider.log("Documentation generated in output/documentation.md")