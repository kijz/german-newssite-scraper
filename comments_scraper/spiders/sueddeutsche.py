# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from comments_scraper.items import CommentItem

class SueddeutscheSpider(scrapy.Spider):
    name = 'sueddeutsche'
    allowed_domains = ['disqus.com']
    #    start_urls = ['https://disqus.com/home/forum/szde/']

    start_urls = ['https://disqus.com/home/discussion/szde/schulz_zukunftsplan/']
    custom_settings = {"DOWNLOADER_MIDDLEWARES": {'comments_scraper.middlewares.JSMiddleware': 543,},}

    rules = [
        Rule(LinkExtractor(allow=['\/home\/discussion\/szde\/\w*\/']),
        callback='parse_site',
        follow=True)
    ]
    def parse(self, response):
        print(response.body)
        selector_list = response.xpath("//LI[@class='post']")
        article_link = response.url

        for selector in selector_list:
            print (selector)
            #comment = self.create_comment(article_link, selector)
            #yield comment

    def parse_site(self, response):
        selector_list = response.css('ul#post-list>.post')
        article_link = response.url

        for selector in selector_list:
            comment = self.create_comment(article_link, selector)
            yield comment

    def create_comment(self, comment_selector):
        comment = CommentItem()
        comment['user_name'] = article_link

        #comment['user_name'] = comment_selector.xpath('div/div/header/span/span/span/a/text()').extract_first()
        #comment['user_link'] = comment_selector.xpath('div/div/header/span/span/span/a/@href').extract_first()

        return comment
