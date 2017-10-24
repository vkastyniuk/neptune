# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Company(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    categories = scrapy.Field()
    city = scrapy.Field()
    address = scrapy.Field()
    postal_code = scrapy.Field()
    phone = scrapy.Field()
