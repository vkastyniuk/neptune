# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy import Request

from neptune.items import Company
from scrapy.loader import ItemLoader, Identity
from scrapy.loader.processors import MapCompose, TakeFirst, Compose


class KontaktSpider(scrapy.Spider):
    name = "kontakt"
    allowed_domains = ["kontakt.by"]
    start_urls = ['http://kontakt.by/predprijatija/']

    def parse(self, response):
        for category in response.css('ul.block-li-1'):
            category_name = category.css('li.first-level a::text').extract_first()

            for sub_category in category.css('li:not(.first-level)'):
                sub_category_name = sub_category.css('a::text').extract_first()
                url = sub_category.css('a::attr(href)').extract_first()

                yield Request(response.urljoin(url) + '/', callback=self.parse_sub_category, meta={
                    'category': category_name,
                    'sub_category': sub_category_name
                })

    def parse_sub_category(self, response):
        for selector in response.css('ul#companies li.company-block'):
            url = selector.css('p.lt-item-title a::attr(href)').extract_first()

            company_loader = CompanyLoader(Company(), selector=selector)
            company_loader.add_value('id', self._get_company_id(url))
            company_loader.add_value('url', response.urljoin(url))
            company_loader.add_css('name', 'p.lt-item-title a::text')
            company_loader.add_css('phone', 'ul.adress li:not(:first-child)::text')
            company_loader.add_css('categories', 'ul.categories li a::text')

            address_string = selector.css('ul.adress li span::text').extract_first()
            if address_string:
                match = re.search('(.*), ([^,]+), (\d+)', address_string.strip())
                if match:
                    company_loader.add_value('address', match.group(1))
                    company_loader.add_value('city', match.group(2))
                    company_loader.add_value('postal_code', match.group(3))

            yield company_loader.load_item()

        next_page_url = response.css('.pages > a.page-selected + a::attr(href)').extract_first()
        if next_page_url:
            yield Request(response.urljoin(next_page_url), callback=self.parse_sub_category, meta={
                'category': response.meta['category'],
                'sub_category': response.meta['sub_category']
            })

    @staticmethod
    def _get_company_id(url):
        match = re.search('/company/(\d+)-', url)
        if match:
            return match.group(1)


class CompanyLoader(ItemLoader):
    default_input_processor = MapCompose(lambda x: x.strip().replace('\n', ''))
    default_output_processor = TakeFirst()

    categories_out = Identity()
    postal_code_out = Compose(TakeFirst(), int)
    phone_in = MapCompose(lambda x: re.sub(u' |\xa0', '', x))
