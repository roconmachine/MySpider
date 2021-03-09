import uuid
import scrapy

from ..items import ShoppingSiteItem, Menu

import logging


class Ghorebazar(scrapy.Spider) :
    name = 'ghorebazar'
    base_url = 'https://www.ghorebazar.com'
    next_page = 1
    menus = []

    def start_requests(self):
        logging.info("start from base url")
        yield scrapy.Request(self.base_url)


    def parse(self, response):
        nav_items = response.css('.full-navigation').xpath('li')
        for item in nav_items :
            categoryNames = []
            self.findCategory(item, categoryNames)
        for menu in self.menus:
            logging.info(menu['menuUrl'])
            logging.info(menu['category'])
            yield scrapy.Request(url=menu['menuUrl'], callback=self.parseCategory, meta={'menu' : menu})



    def findCategory(self, category, categoryName):
        a = category.xpath('a').extract()
        if len(category.xpath('a').extract()) > 0 :
            categoryName.append(category.xpath('a/text()').extract_first())
        else :
            return
        sub = category.css('ul').xpath('li')
        if len(sub) > 0 :
            for subItem in sub :
                self.findCategory(subItem,categoryName)
        else :
            menu = Menu()
            menu['category'] = categoryName[:]
            menu['menuUrl'] = self.base_url +'/'+ str(category.xpath('a/@slug').extract_first())
            self.menus.append(menu)
            del categoryName[len(categoryName) - 1]

    def parseCategory(self, response):
        for product in response.css('.product-card') :
            item = ShoppingSiteItem()
            item['crawl_id'] = getattr(self, "crawl_id", str(uuid.uuid1()))
            item['category'] = response.meta['menu']['category']
            item['category_id'] = ' >> '.join(item['category'])
            item['imgUrl'] = product.css('img::attr(src)').get()
            item['quantity'] = product.css('.running-offer-desc::text').extract_first()
            item['price'] = product.css('.product-card-price::text').extract_first()
            item['productUrl'] = self.base_url + "/" + product.css('h1 a::attr(href)').extract_first()
            item['lang'] = 'ENG'
            item['location'] = 'Dhaka'
            item['site_name'] = 'ghorebazar.com'
            item['size'] = 'n/a'
            item['details'] = 'n/a'
            item['title'] = product.css('h1 a::text').extract_first()

            yield item
