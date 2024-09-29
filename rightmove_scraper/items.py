"""
See documentation:  http://doc.scrapy.org/en/latest/topics/items.html
"""

import copy
from re import compile

import datetime
from scrapy import Item, Field
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst

from rightmove_scraper import models


# ----------------------------------------------------------------------------
# Processors
# ----------------------------------------------------------------------------
#

PRICE_RE = compile(r"£(\d+),(\d+) pcm")
ADDED_ON_RE = compile(r"Added on (\d+/\d+/\d+)")


def price(text: str):
    if (price_match := PRICE_RE.match(text)) is not None:
        return int("".join(map(str, price_match.groups([1, 2]))))
    else:
        return None


def added_on(text: str):
    addedOn = ADDED_ON_RE.match(text)
    if addedOn:
        return datetime.datetime.strptime(addedOn.group(1), "%d/%m/%Y").date()
    else:
        return None


def strip_whitespace(text):
    text = str(text).replace("\n", " ").replace("\r", " ").strip()
    if text == "":
        return None
    return text


# ----------------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------------


class DefaultLoader(ItemLoader):
    default_input_processor = MapCompose(strip_whitespace)
    default_output_processor = TakeFirst()


class ModelItem(Item):

    def __init__(self, model=None, **kwds):
        super(ModelItem, self).__init__()

        if model:
            self.__model__ = model

        if "Meta" in dir(self):
            for key, processor in self.Meta.__dict__.items():
                if not key.startswith("__"):
                    kwds[key] = processor

        for key in self.model._meta.fields.keys():
            self.fields[key] = Field()

        if kwds is not None:
            for key, processor in kwds.items():
                self.fields[key] = Field(
                    input_processor=MapCompose(strip_whitespace, processor)
                )

    def __setitem__(self, key, value):
        if key not in self.fields:
            self.fields[key] = Field()
        self._values[key] = value

    def copy(self):
        return copy.deepcopy(self)

    def save(self):
        return self.model.from_scrapy_item(self)

    @property
    def model(self):
        return self.__model__


# ----------------------------------------------------------------------------
# Items
# ----------------------------------------------------------------------------


class Agency(ModelItem):
    __model__ = models.Agency


class Property(ModelItem):
    __model__ = models.Property

    class Meta:
        addedOn = added_on
        price = price


class KeyFeature(ModelItem):
    __model__ = models.KeyFeature


class Image(ModelItem):
    __model__ = models.Image


class Floorplan(ModelItem):
    __model__ = models.Floorplan


class Brochure(ModelItem):
    __model__ = models.Brochure


class Video(ModelItem):
    __model__ = models.Video
