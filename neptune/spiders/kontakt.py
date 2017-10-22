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
        categories = response.css('ul.block-li-1').extract()

        for category in categories:
            category_name = category.css('li.first-level a::text').extract_first()
            sub_categories = category.css('li:not(.first-level)').extract()

            for sub_category in sub_categories:
                sub_category_name = sub_category.css('a::text').extract_first()
                url = sub_category.css('a::attr(href)').extract_first()

                yield Request(url, callback=self.parse_sub_category, meta={
                    'category': category_name,
                    'sub_category': sub_category_name
                })

    def parse_sub_category(self, response):
        companies = response.css('ul#companies li.company-block').extract()
        for company in companies:
            name = company.css('p.lt-item-title a::text').extract_first()
            url = company.css('p.lt-item-title  a::attr(href)').extract_first()

            address_string = company.css('ul.adress li span::text').extract_first()
            match = re.search('(.*), ([^,]+), (\d+)$', address_string)
            if match:
                address = match.group(1)
                city = match.group(2)
                postal_code = match.group(3)

            phone = company.css('ul.adress li:not(:first-child)::text').extract_first()

            categories = []
            for category in company.css('ul.categories li').extract():
                category_name = category.css('a::text').extract_first()
                categories.append(category_name)

            yield Company(name=name, url=url, city=city, address=address, postal_code=postal_code, phone=phone, categories=categories)
