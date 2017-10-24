# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy import Request

from neptune.items import Company


class KontaktSpider(scrapy.Spider):
    name = "kontakt"
    allowed_domains = ["kontakt.by"]
    start_urls = ['http://kontakt.by/predprijatija/']

    def parse(self, response):
        categories = response.css('ul.block-li-1')

        for category in categories:
            category_name = category.css('li.first-level a::text').extract_first()
            sub_categories = category.css('li:not(.first-level)')

            for sub_category in sub_categories:
                sub_category_name = sub_category.css('a::text').extract_first()
                url = sub_category.css('a::attr(href)').extract_first()

                yield Request(response.urljoin(url)+'/', callback=self.parse_sub_category, meta={
                    'category': category_name,
                    'sub_category': sub_category_name
                })

    def parse_sub_category(self, response):
        companies = response.css('ul#companies li.company-block')
        for company in companies:
            name = company.css('p.lt-item-title a::text').extract_first().strip()
            url = company.css('p.lt-item-title  a::attr(href)').extract_first()

            address_string = company.css('ul.adress li span::text').extract_first()
            if address_string:
                match = re.search('(.*), ([^,]+), (\d+)', address_string.strip())
                if match:
                    address = match.group(1)
                    city = match.group(2)
                    postal_code = int(match.group(3))

            phone = company.css('ul.adress li:not(:first-child)::text').extract_first()

            categories = []
            for category in company.css('ul.categories li'):
                category_name = category.css('a::text').extract_first().strip()
                categories.append(category_name)

            yield Company(name=name, url=url, city=city, address=address, postal_code=postal_code, phone=phone, categories=categories)

        next_page_url = response.css('.pages > a.page-selected + a::attr(href)').extract_first()
        if next_page_url:
            yield Request(response.urljoin(next_page_url), callback=self.parse_sub_category, meta={
                'category': response.meta['category'],
                'sub_category': response.meta['sub_category']
            })
