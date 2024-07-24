import jsonschema
from scrapy.exceptions import DropItem

class DataValidationPipeline:
    def process_item(self, item, spider):
        schema = {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "content": {"type": "string"},
                "content_hash": {"type": "string"}
            },
            "required": ["url", "content", "content_hash"]
        }
        try:
            jsonschema.validate(instance=item, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            spider.logger.error(f"Data validation error: {e}")
            return None
        return item

class DuplicateFilterPipeline:
    def __init__(self):
        self.seen_hashes = set()

    def process_item(self, item, spider):
        if item['content_hash'] in self.seen_hashes:
            raise DropItem(f"Duplicate item found: {item}")
        self.seen_hashes.add(item['content_hash'])
        return item

class ExportPipeline:
    def process_item(self, item, spider):
        # Implement export logic for different formats here
        return item