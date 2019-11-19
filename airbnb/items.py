# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AirbnbItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    boxtime = scrapy.Field()
    region = scrapy.Field()
    rank = scrapy.Field()
    title = scrapy.Field()
    chtitle = scrapy.Field()
    gross = scrapy.Field()
    rating = scrapy.Field()
