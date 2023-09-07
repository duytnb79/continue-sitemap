# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field
from json import JSONEncoder


class CrawlTestItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    pass


class PageInfoItem(Item):
    URL = Field()
    title = Field()
    meta = Field()
    h1 = Field()
    html_compressed_bytes = Field()
    html_compressed = Field()
    id = Field()
    pass


# subclass JSONEncoder
class Encoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
