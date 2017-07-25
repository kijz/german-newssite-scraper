# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from comments_scraper.items import CommentItem
import logging
import time

class ZeitSpider(CrawlSpider):
    name = 'zeit'
    allowed_domains = ['www.zeit.de', 'community.zeit.de']
    start_urls = ['http://www.zeit.de/wissen/2017-07/suche-ausserirdische-aliens-weltraum-kontakt-meti']

    custom_settings = {"DOWNLOADER_MIDDLEWARES": {'comments_scraper.middlewares.JSMiddleware': 543,},}

    rules = [
        Rule(LinkExtractor(allow=['/wissen/2017-07/suche-ausserirdische-aliens-weltraum-kontakt-meti\?page=\d*']),
        callback='parse_site',
        follow=True)#,
        #Rule(LinkExtractor(allow=['/user/.*']),
        #follow=True)
    ]

    def parse_site(self, response):
        selector_list = response.css('div.comment__container')
        article_link = response.url
        for selector in selector_list:
            comment = self.create_comment(article_link, selector)
            yield comment

    def create_comment(self, article_link, comment_selector):
        comment = CommentItem()
        comment['user_name'] = comment_selector.xpath("div[@class='comment-meta']/div[@class='comment-meta__name']/a/text()").extract_first()
        comment['content'] = comment_selector.xpath("div[@class='comment__body']/p/text()").extract()
        comment['upvotes'] = comment_selector.xpath("//span[@class='js-comment-recommendations']/text()").extract_first()
        comment['comment_link'] = article_link
        return comment
