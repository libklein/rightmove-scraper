from rightmove_scraper.items import ModelItem
from playhouse.shortcuts import model_to_dict
from scrapy.exporters import JsonLinesItemExporter


class DBJsonExporter(JsonLinesItemExporter):
    def export_item(self, item):
        if isinstance(item, ModelItem):
            model = item.model.get_by_id(item[item.model._meta.primary_key.name])
            super().export_item(model_to_dict(model, backrefs=True))
