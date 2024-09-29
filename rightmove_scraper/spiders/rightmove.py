# coding=utf-8

import datetime
import json
from typing import Dict, Iterable, Union, Optional
from urllib import parse as urlparse

import scrapy  # type: ignore
from scrapy.http.response import Response  # type: ignore

from rightmove_scraper.items import DefaultLoader as ItemLoader
from rightmove_scraper.items import (
    Property,
    KeyFeature,
    Agency,
    Floorplan,
    Brochure,
    Image,
    Video,
)

PR = Iterable[Union[Dict, scrapy.Request]]


def _extract_model(response: Response) -> Dict:
    script = response.xpath(
        "/html/body/script[text()[contains(.,'window.jsonModel = ')]]/text()"
    ).extract_first()
    jsmodel = script[len("window.jsonModel = ") :]
    model = json.loads(jsmodel)
    return model


def _extract_property_model(response: Response) -> Dict:
    script = (
        response.xpath(
            "/html/body/script[text()[contains(.,'window.PAGE_MODEL = ')]]/text()"
        )
        .extract_first()
        .strip()
    ).split("\n")[0]
    jsmodel = script[len("window.PAGE_MODEL = ") :]
    model = json.loads(jsmodel)
    return model


def _get_pages(response: Response, model: Dict) -> Iterable[str]:
    url = response.url
    pagination = model["pagination"]
    options = pagination["options"]

    qr = urlparse.urlparse(url)
    parsed = list(qr)
    qs = urlparse.parse_qs(qr.query)

    # ignore first page. We only parse pages once, by loading the first page.
    for option in options[1:]:
        newqs = qs.copy()
        newqs["index"] = option["value"]
        newquery = urlparse.urlencode(newqs, doseq=True)
        parsed[4] = newquery
        yield urlparse.urlunparse(parsed)


# Function to load property data
def load_property_data(property_data):
    loader = ItemLoader(item=Property())

    field_mapping = {
        "id": property_data["id"],
        "bathrooms": property_data["bathrooms"],
        "bedrooms": property_data["bedrooms"],
        "property_type": property_data["propertySubType"],
        "deposit": property_data["lettings"]["deposit"],
        "furnish_type": property_data["lettings"]["furnishType"],
        "let_available_date": property_data["lettings"]["letAvailableDate"],
        "let_type": property_data["lettings"]["letType"],
        "minimum_term_in_months": property_data["lettings"]["minimumTermInMonths"],
        "display_address": property_data["address"]["displayAddress"],
        "postcode": f"{property_data['address']['outcode']} {property_data['address']['incode']}",
        "latitude": property_data["location"]["latitude"],
        "longitude": property_data["location"]["longitude"],
        "price": property_data["prices"]["primaryPrice"],
        "status": (
            "LET_AGREED"
            if "LET_AGREED" in property_data["tags"]
            else (
                "OFF_THE_MARKET" if property_data["status"]["archived"] else "AVAILABLE"
            )
        ),
        "added_on": property_data["listingHistory"]["listingUpdateReason"],
    }

    for field, value in field_mapping.items():
        loader.add_value(field, value)

    return loader


# Function to load agency data
def load_agency_data(agency_data):
    loader = ItemLoader(item=Agency())
    loader.add_value("id", agency_data["branchId"])
    loader.add_value("name", agency_data["branchDisplayName"])
    return loader.load_item()


# Function to load key features
def load_key_features(key_features, property_item: Property):
    items = []
    for feature in key_features:
        loader = ItemLoader(item=KeyFeature())
        loader.add_value("feature", feature)
        loader.add_value("property", property_item)
        items.append(loader.load_item())
    return items


# Function to load related data like images, floorplans, brochures, and videos
def load_related_data(item_class, data_items, property: Property, url_key="url"):
    items = []
    for item in data_items:
        loader = ItemLoader(item=item_class())
        loader.add_value("url", item[url_key])
        loader.add_value("property_id", property['id'])
        items.append(loader.load_item())
    return items


def parse_property_data(property_data: dict):
    # Load the property data
    property_loader = load_property_data(property_data)

    # Load the agency data and add it to the property
    agency_item = load_agency_data(property_data["customer"])
    property_loader.add_value("agency_id", agency_item['id'])

    property_item = property_loader.load_item()

    nested_items = [agency_item]
    # Load key features and add them to the property
    nested_items.extend(load_key_features(property_data["keyFeatures"], property_item))

    related_data = [
        (Image, property_data["images"]),
        (Floorplan, property_data["floorplans"]),
        (Brochure, property_data["brochures"]),
        (Video, property_data["virtualTours"]),
    ]

    for item_class, data in related_data:
        nested_items.extend(load_related_data(item_class, data, property_item))

    # Load and yield all nested items
    for item in nested_items:
        yield item
    # Finally yield the property item
    yield property_item


class RightmoveSpider(scrapy.Spider):
    name: str = "rightmove"
    allowed_domains = ["rightmove.co.uk"]

    def start_requests(self) -> Iterable[scrapy.Request]:
        urls = self.settings.get("SEARCH_URLS", [])
        if isinstance(urls, str):
            urls = urls.split(",")
        if len(urls) == 0:
            print("No search URLs configured. Please set SEARCH_URLS in settings.py.")

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response, *args, **kwargs) -> PR:
        model = _extract_model(response)
        for page in _get_pages(response, model):
            yield scrapy.Request(page, callback=self.parse_page)

        yield from self.parse_propertymodel(response, model)

    def parse_page(self, response: Response) -> PR:
        model = _extract_model(response)
        yield from self.parse_propertymodel(response, model)

    def parse_propertymodel(self, response: Response, model: Dict) -> PR:
        properties = model["properties"]
        for data in properties:
            yield response.follow(data["propertyUrl"], callback=self.parse_property)

    def parse_property(self, response: Response) -> PR:
        model = _extract_property_model(response)

        propertyData = model["propertyData"]

        yield from parse_property_data(propertyData)
