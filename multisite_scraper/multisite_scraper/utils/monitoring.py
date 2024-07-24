import logging

def log_crawl_status(current_page, max_pages):
    progress = (current_page / max_pages) * 100
    logging.info(f"Crawl progress: {progress:.2f}% ({current_page}/{max_pages})")