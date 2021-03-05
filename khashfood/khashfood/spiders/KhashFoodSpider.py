import uuid
import scrapy

from ..items import ShoppingSiteItem

import logging

class KhashFoodSpider(scrapy.Spider) :

    name = 'khashfood'
    base_url = 'https://www.khaasfood.com/shop/'
    next_page = 1


    def start_requests(self):
        yield scrapy.Request(self.base_url)

    def parse (self, response) :
        logging.info("parse khashfood start --")
        categories_container = response.css('.woodmart-product-categories')
        categories = categories_container.xpath('li')
        for cat in categories :
            arrcatNames = []
            self.parseCategory(cat, arrcatNames)

    def parseCategory(self, cat, arrcatNames) :
        if cat.css('.category-name::text').extract_first() == 'All' :
            return
        arrcatNames.append(cat.css('.category-name::text').extract_first())

        children = cat.css('.children li')
        if len(children) > 0 :
            for child in children :
                self.parseCategory(child,arrcatNames)
        else:
            p_categories_link = cat.css('a::attr(href)').get()
            logging.info(p_categories_link)
            logging.info(arrcatNames)
            request = scrapy.Request(p_categories_link, callback=self.parseCategoryLink)
            request.meta["categories"] = arrcatNames
            yield request




    def parseCategoryLink(self, response ):

        crawl_id = getattr(self, "crawl_id", str(uuid.uuid1()))
        products = response.css('div.product-grid-item')

        for product in products:
            item = ShoppingSiteItem()
            item['crawl_id'] = crawl_id
            item['category'] = response.meta['categories']
            item['title'] = product.css('.product-title').css('a::text').extract_first()
            item['productUrl'] = product.css('.product-title').css('a::attr(href)').extract_first()

            item['imgUrl'] = product.css('img::attr(data-wood-src)').extract_first()
            multiple_option = False
            if len(product.css('.woocommerce-Price-amount bdi::text').extract()) > 1:
                multiple_option = True
            else:
                item['price'] = product.css('.woocommerce-Price-amount bdi::text').extract_first()
                item['quantity'] = product.css('.product_quantity::text').extract_first()

            # logging.info(item['productUrl'])
            # yield item
            yield response.follow(str(item['productUrl']), method='GET', callback=self.parse_details,
                                  meta=dict(item=item, options=multiple_option))
        # end of for loop
        page = response.meta.get('page', 1) + 1

        next_url = self.base_url + 'page/' + str(page) + '/'
        yield scrapy.Request(next_url, meta=dict(page=page))


    def parse_details(self, response) :

        item = response.meta.get('item')
        # item['category'] = response.css('.posted_in a::text').extract()
        # item['category'] = ','.join(map(str, categories))
        item['lang'] = 'ENG'
        item['location'] = 'Dhaka'
        item['site_name'] = self.base_url
        item['size'] = 'n/a'
        item['details'] = str(response.css('.woocommerce-product-details__short-description div::text').extract_first()).strip()
        if len(item['details']) > 0 :
            item['details'] = response.css('.woocommerce-product-details__short-description p::text').extract_first()

        if response.meta.get('options') :
            prices = response.css('.summary-inner bdi::text').extract()
            qts = response.css('select option::attr(value)').extract()
            qts =  [i for i in qts if i]
            for price in prices :
                item['price'] = str(price)
                item['quantity'] = qts[0]
                del qts[0]
                yield item

        else :
            yield item