# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ImageItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_names = scrapy.Field()

class ShoppingSiteItem(scrapy.Item):
    # define the fields for your item here like:
    crawl_id = scrapy.Field()
    site_name  = scrapy.Field()
    category  = scrapy.Field()
    category_id  = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    quantity  = scrapy.Field()
    size = scrapy.Field()
    details = scrapy.Field()
    imgUrl = scrapy.Field()
    productUrl = scrapy.Field()
    lang = scrapy.Field()
    location = scrapy.Field()