import uuid
import scrapy
from ..items import ShoppingSiteItem, Menu
import logging
class Eonbazar(scrapy.Spider) :
    name = 'eonbazar'
    base_url = 'https://eonbazar.com/'
    next_page = 1
    menus = []


    def start_requests(self):
        logging.info("start from base url")
        yield scrapy.Request(self.base_url)

    def parse(self, response, **kwargs):

        menus = response.css('.groupmenu li').css('.cat-tree')
        for menu in menus :
            arrCategory = []
            self.parseCategory(menu, arrCategory)

        for menu in self.menus:
            logging.info(menu['menuUrl'])
            logging.info(menu['category'])
            yield scrapy.Request(url=menu['menuUrl'], callback=self.parseProduct, meta={'menu': menu})



    def parseCategory(self, categoryElement, arrCategory):

        logging.info(categoryElement)
        if type(categoryElement) == "<class 'str'>" :
            return
        if len(categoryElement.xpath('a').css('span')) == 1 :
            arrCategory.append(categoryElement.xpath('a').css('span::text').extract_first())
        else :
            arrCategory.append(categoryElement.xpath('a').xpath('span').css('.link-text').extract_first())

        if len(categoryElement.css('ul').extract()) > 0 :
            for menu in categoryElement.css('ul li') :
                self.parseCategory(menu, arrCategory)
        else :
            menu = Menu()
            menu['category'] = arrCategory[:]
            menu['menuUrl'] = categoryElement.css('a::attr(href)').extract_first()
            self.menus.append(menu)
            del arrCategory[len(arrCategory) - 1]


    def parseProduct(self, response):
        for product in response.css('.products').xpath('ol').xpath('li')  :
            item = ShoppingSiteItem()
            item['crawl_id'] = getattr(self, "crawl_id", str(uuid.uuid1()))
            item['category'] = response.meta['menu']['category']
            item['category_id'] = ' >> '.join(item['category'])
            item['lang'] = 'ENG'
            item['location'] = 'Dhaka'
            item['site_name'] = 'eonbazar.com'
            item['size'] = 'n/a'

            item['title'] = product.css('.product-item-link::text').get().strip()
            arrStr = []
            for img in product.css(".product-image-photo::attr('src')").extract() :
                arrStr.append(self.base_url + img)
            item['imgUrl'] = arrStr
            item['quantity'] = 'n/a'
            item['price'] = product.css('.price::text').get().replace('BDT', '').strip()

            item['productUrl'] = product.css('.product-item-link::attr(href)').get()
            item['details'] = 'n/a'


            yield item