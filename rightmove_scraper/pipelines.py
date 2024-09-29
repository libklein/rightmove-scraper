"""
Save ModelItem's to a local SQLite database.
"""

from collections import defaultdict

from peewee import chunked

from rightmove_scraper.items import ModelItem, Property
from rightmove_scraper.exporters import DBJsonExporter
from os import environ


class ModelPipeline:
    "The pipeline stores scraped data in a database."

    def open_spider(self, spider):
        self.models = defaultdict(list)

    def close_spider(self, spider):
        if len(self.models):
            for model_name, list_of_models in self.models.items():
                model = list_of_models[0].model
                for batch in chunked(list_of_models, 25):
                    try:
                        model.insert_many(batch).on_conflict_replace().execute()
                    except Exception as e:
                        print(f"Failed to insert {len(batch)} {model_name} models: {e}")
            if spider.settings.get("OUTPUT_JSON_PATH"):
                exporter = DBJsonExporter(open(spider.settings.get("OUTPUT_JSON_PATH"), 'wb'))
                exporter.start_exporting()
                for item in self.models[Property]:
                    exporter.export_item(item)
                exporter.finish_exporting()

    def process_item(self, item, spider):
        if isinstance(item, ModelItem):
            model_name = type(item)
            self.models[model_name].append(item)
        return item
