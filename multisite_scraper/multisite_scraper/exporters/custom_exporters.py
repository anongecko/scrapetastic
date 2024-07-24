from scrapy.exporters import JsonItemExporter, CsvItemExporter, XmlItemExporter

class CustomJsonExporter(JsonItemExporter):
    def __init__(self, file, **kwargs):
        super().__init__(file, ensure_ascii=False, indent=2, **kwargs)

class CustomCsvExporter(CsvItemExporter):
    pass

class CustomXmlExporter(XmlItemExporter):
    pass