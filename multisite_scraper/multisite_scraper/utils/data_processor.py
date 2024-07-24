import hashlib

def process_data(content, url):
    # Implement any data processing logic here
    processed_data = {
        'url': url,
        'content': content,
        'content_hash': hashlib.md5(content.encode()).hexdigest()
    }
    return processed_data