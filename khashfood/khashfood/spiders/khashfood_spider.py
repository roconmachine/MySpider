import uuid
import scrapy

from ..items import ShoppingSiteItem

import logging

class KhashFoodSpider(scrapy.Spider) :

    name = 'backup_spider'
    base_url = 'https://www.khaasfood.com/shop/'
    next_page = 1


    def start_requests(self):
        yield scrapy.Request(self.base_url)

    def parse (self, response) :

        crawl_id = getattr(self, "crawl_id", str(uuid.uuid1()))
        products = response.css('div.product-grid-item')


        for product in products :
            item = ShoppingSiteItem()
            item['crawl_id'] = crawl_id
            item['title'] = product.css('.product-title').css('a::text').extract_first()
            item['productUrl'] = product.css('.product-title').css('a::attr(href)').extract_first()


            item['imgUrl'] = [product.css('img::attr(data-wood-src)').extract_first()]
            multiple_option = False
            if len(product.css('.woocommerce-Price-amount bdi::text').extract()) > 1:
                multiple_option = True
            else:
                item['price'] = product.css('.woocommerce-Price-amount bdi::text').extract_first()
                item['quantity'] = product.css('.product_quantity::text').extract_first()

            # logging.info(item['productUrl'])
            # yield item
            yield response.follow(str(item['productUrl']), method='GET', callback=self.parse_details, meta=dict(item=item, options= multiple_option))
        # end of for loop
        page = response.meta.get('page', 1) + 1

        next_url = self.base_url + 'page/' + str(page) + '/'
        yield scrapy.Request(next_url, meta=dict(page = page))



    def parse_details(self, response) :

        item = response.meta.get('item')
        item['category'] = response.css('.posted_in a::text').extract()
        item['category_id'] = ' >> '.join(item['category'])
        item['lang'] = 'ENG'
        item['location'] = 'Dhaka'
        item['site_name'] = 'khaasfood.com'
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