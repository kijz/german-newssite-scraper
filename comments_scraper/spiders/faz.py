# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from comments_scraper.items import CommentItem
import logging

class FazSpider(CrawlSpider):
    name = 'faz'
    allowed_domains = ['faz.net']
    start_urls = ['http://www.faz.net/aktuell/']
    custom_settings = {"DOWNLOADER_MIDDLEWARES": {'comments_scraper.middlewares.JSMiddleware': 543,},}

    rules = [
        Rule(LinkExtractor(allow=['/\w*/\w*/.*.html']),
        callback='parse_site',
        follow=True),
        Rule(LinkExtractor(allow=['/suche/.*']),
        follow=True)
    ]

    #def parse(self, response):
    #    pass

    def parse_site(self, response):
        selector_list = response.css('div#TabLesermeinungContent_AlleMeinungen>.LMFuss')
        article_link = response.url

        for selector in selector_list:
            print (selector)
            comment = self.create_comment(article_link, selector)
            yield comment

    def create_comment(self, article_link, comment_selector):
        nameArray = comment_selector.xpath('span[@class="Username"]/a/span/span[@class="truncate truncate300"]/text()').extract_first()

        comment = CommentItem()
        comment['user_name'] = comment_selector.xpath('span[@class="Username"]/a/@data-loginname').extract_first()
        if nameArray:
            nameArray = nameArray.split()
            comment['fore_name'] = nameArray[0]
            comment['last_name'] = nameArray[1]
        comment['upvotes'] = comment_selector.xpath('span/span[@class="recommsAmount"]/text()').extract_first()
        comment['recommendations'] = comment_selector.xpath('span[@class="Username"]/a/span/span[@class="greenTxt truncate bold"]/text()').extract_first()
        comment['date'] = self.format_date(comment_selector.xpath('span[@class="Username"]/span[@class="grayTxt dateTime"]/text()').extract_first())
        comment['user_link'] = self.set_faz_link(comment_selector.xpath('span[@class="Username"]/a/@href').extract_first())
        comment['comment_link'] = None
        comment['article_link'] = article_link
        comment['title'] = comment_selector.xpath('span[@class="LMFussLink"]/text()').extract_first()
        comment['content'] = self.glue_string_array(comment_selector.xpath('div[@class="LMText"]/text()').extract())
        comment['quote'] = self.get_answers(comment_selector.xpath('div[@class="LMText"]/div[@class="LMAntwortWrapper"]/div'))
        return comment

    def get_answers(self, answer_selectors):
        answerArray = []
        if answer_selectors:
            for answer_selector in answer_selectors:
                answerArray.append(self.create_comment(None, answer_selector))
        return answerArray

    def format_date(self, date_string):
        return date_string[3:]

    def glue_string_array(self, array):
        glued = " ".join(array)
        return (" ".join(glued.split()))

    def set_faz_link(self, link):
        if link:
            return ('http://www.faz.net%s' % str(link))
