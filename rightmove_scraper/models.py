"""
Models to store scraped data in a database.
"""

import inspect
from os import environ

from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    IntegerField,
    FloatField,
    DateField,
    TextField,
    ForeignKeyField,
)


db = SqliteDatabase(environ.get("DB_PATH", "rightmove.db"))


class BaseModel(Model):
    class Meta:
        database = db

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __delitem__(self, key):
        return setattr(self, key, None)

    @classmethod
    def primary_keys(cls):
        pk = cls._meta.primary_key
        if "field_names" in pk.__dict__:
            names = pk.field_names
        else:
            names = (pk.name,)
        return names

    @classmethod
    def from_scrapy_item(cls, item):
        query = cls.insert(**item).on_conflict("REPLACE")
        return query.execute()


# ----------------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------------


class Agency(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()

    class Meta:
        db_table = "agencies"


class Property(BaseModel):
    id = IntegerField(primary_key=True)

    # Rooms and letting details
    bathrooms = IntegerField(null=True)
    bedrooms = IntegerField(null=True)
    property_type = CharField(null=True)
    deposit = IntegerField(null=True)
    furnish_type = CharField(null=True)
    let_available_date = DateField(null=True)
    let_type = CharField(null=True)
    minimum_term_in_months = IntegerField(null=True)

    # Address and location
    display_address = CharField(null=True)
    postcode = CharField(null=True)
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)

    # Price
    price = IntegerField(null=True)

    # Metadata
    status = CharField()
    added_on = DateField(null=True)

    # Foreign key for agency
    agency_id = ForeignKeyField(Agency, backref="properties")

    class Meta:
        db_table = "properties"


class KeyFeature(BaseModel):
    property = ForeignKeyField(Property, backref="key_features")
    feature = TextField()

    class Meta:
        db_table = "key_features"


class Image(BaseModel):
    property_id = ForeignKeyField(Property, backref="images")
    url = CharField()

    class Meta:
        db_table = "images"


class Floorplan(BaseModel):
    property_id = ForeignKeyField(Property, backref="floorplans")
    url = CharField()

    class Meta:
        db_table = "floorplans"


class Brochure(BaseModel):
    property_id = ForeignKeyField(Property, backref="brochures")
    url = CharField()

    class Meta:
        db_table = "brochures"


class Video(BaseModel):
    property_id = ForeignKeyField(Property, backref="videos")
    url = CharField()

    class Meta:
        db_table = "videos"


# ----------------------------------------------------------------------------
# Automatically create the tables...
# ----------------------------------------------------------------------------


def create_tables():
    models = []
    for name, cls in globals().items():
        if inspect.isclass(cls) and issubclass(cls, BaseModel):
            if name == "BaseModel":
                continue
            models.append(cls)
    db.create_tables(models, safe=True)


if __name__ == "__main__":
    create_tables()
