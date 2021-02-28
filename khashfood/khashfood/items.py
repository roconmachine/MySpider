# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# {
#                     "crawl_id": crawl_id,
#                     "site_name": "meenaclick.com",
#                     "category": category,
#                     "category_id": category_id,
#                     "title" : title.strip(),
#                     "quantity" : qty,
#                     "size" : "",
#                     "price" : price,
#                     "details" : details,
#                     "imgUrl" : [img_url],
#                     "productUrl" : product_url,
#                     "lang": 'ENG',
#                     "location": city
#                 }


class KhashfoodItem(scrapy.Item):
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

def __init__(self):
    self['lang'] = 'ENG'
    self['location'] = "Dhaka"









