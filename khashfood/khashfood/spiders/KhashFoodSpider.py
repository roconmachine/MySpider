import uuid
import scrapy

from ..items import ShoppingSiteItem, Menu

import logging


class KhashFoodSpider(scrapy.Spider):
    name = 'khashfood'
    base_url = 'https://www.khaasfood.com/shop/'
    next_page = 1
    menus = []

    def start_requests(self):
        yield scrapy.Request(self.base_url)

    def parse(self, response):
        logging.info("parse khashfood start --")
        categories_container = response.css('.woodmart-product-categories')
        categories = categories_container.xpath('li')
        for cat in categories:
            arrcatNames = []
            self.parseCategory(cat, arrcatNames)

        # logging.info("menus ........")
        # menu = self.menus[1]  # for testing purpose
        for menu in self.menus:
            logging.info(menu['menuUrl'])
            logging.info(menu['category'])
            yield scrapy.Request(url=menu['menuUrl'], callback=self.parseCategoryLink,
                                 meta={'categories': menu['category'], 'catUrl': menu['menuUrl']}, dont_filter=True)

    def parseCategory(self, cat, arrcatNames):

        if cat.css('.category-name::text').extract_first() == 'All':
            return
        if 'wc-default-cat' in cat.xpath('@class').extract_first() :
            return
        # wc - default - cat
        arrcatNames.append(cat.css('.category-name::text').extract_first())

        children = cat.css('.children li')
        if len(children) > 0:
            for child in children:
                self.parseCategory(child, arrcatNames)


        else:
            p_categories_link = cat.css('a::attr(href)').get()

            menu = Menu()
            menu['category'] = arrcatNames[:]
            menu['menuUrl'] = p_categories_link
            self.menus.append(menu)
            del arrcatNames[len(arrcatNames) - 1]
            # logging.log("parse : " + url)
            # yield scrapy.Request(url=url, callback=self.parseCategoryLink , meta={'categories' : arrcatNames})
            # option 2
            # yield response.follow(url= p_categories_link, callback=self.parseCategoryLink, meta={'categories' : arrcatNames})

    def parseCategoryLink(self, response):

        crawl_id = getattr(self, "crawl_id", str(uuid.uuid1()))
        products = response.css('div.product-grid-item')

        for product in products:
            # if product.css('.out-of-stock::text ').extract_first() == 'Sold out' :
            #     continue
            item = ShoppingSiteItem()
            item['crawl_id'] = crawl_id
            item['category'] = response.meta['categories']
            item['category_id'] = ' >> '.join(item['category'])

            item['title'] = product.css('.product-title').css('a::text').extract_first()
            item['productUrl'] = product.css('.product-title').css('a::attr(href)').extract_first()

            item['imgUrl'] = [product.css('img::attr(data-wood-src)').extract_first()]
            multiple_option = False
            if len(product.css('.woocommerce-Price-amount bdi::text').extract()) > 1:
                if len(product.css('.price ins bdi::text').extract()) == 1:
                    item['price'] = product.css('.price ins bdi::text').extract_first()
                    item['quantity'] = product.css('.product_quantity::text').extract_first()
                else:
                    multiple_option = True
            else:
                item['price'] = product.css('.price bdi::text').extract_first()
                item['quantity'] = product.css('.product_quantity::text').extract_first()

            # logging.info(item['productUrl'])
            # yield item
            yield scrapy.Request(str(item['productUrl']), method='GET', callback=self.parse_details,
                                 meta=dict(item=item, options=multiple_option), dont_filter=True)
        # end of for loop

        # page / 2 /
        page = response.meta.get('page', 1) + 1

        next_url = response.meta['catUrl'] + 'page/' + str(page) + '/'
        logging.info("Next page : " + next_url)
        yield scrapy.Request(url=next_url, callback=self.parseCategoryLink,
                             meta=dict(page=page, categories=response.meta['categories'],
                                       catUrl=response.meta['catUrl']), dont_filter=True)

    def parse_details(self, response):

        item = response.meta.get('item')
        # item['category'] = response.css('.posted_in a::text').extract()
        # item['category'] = ','.join(map(str, categories))
        item['lang'] = 'ENG'
        item['location'] = 'Dhaka'
        item['site_name'] = 'khaasfood.com'
        item['size'] = 'n/a'
        item['details'] = str(
            response.css('.woocommerce-product-details__short-description div::text').extract_first()).strip()
        if len(item['details']) > 0:
            item['details'] = response.css('.woocommerce-product-details__short-description p::text').extract_first()

        if response.meta.get('options'):
            prices = response.css('.summary-inner bdi::text').extract()
            qts = response.css('select option::attr(value)').extract()
            qts = [i for i in qts if i]
            # if len(qts) == len(prices) :
            for price in prices:
                item['price'] = str(price)

                item['quantity'] = qts[0]
                del qts[0]
                if item['quantity']:
                    item['quantity'] = item['quantity'].replace('-', ' ')
                yield item

        else:
            if item['quantity'] :
                item['quantity'] = item['quantity'].replace('-', ' ')
            yield item
