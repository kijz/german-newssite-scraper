# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from comments_scraper.items import CommentItem
import time
import datetime

class FocusSpider(CrawlSpider):
    name = 'focus'
    allowed_domains = ['focus.de']
    start_urls = ['http://focus.de/']
    custom_settings = {"DOWNLOADER_MIDDLEWARES": {'comments_scraper.middlewares.JSMiddleware': 543,},}

    rules = [
        Rule(LinkExtractor(allow=['\/\w*\/\w*\/[\w*-]*.html']),
        callback='parse_site',
        follow=True)
    ]

    def parse_site(self, response):
        selector_list = response.css('div.comment')
        article_link = response.url

        print (response.body)
        #for selector in selector_list:
        #    comment = self.create_comment(article_link, selector)
        #    yield comment

    def create_comment(self, article_link, comment_selector):
        time_scraped = time.time()

        comment = CommentItem()
        comment['article_link'] = article_link
        comment['time_stamp'] = datetime.datetime.fromtimestamp(time_scraped).strftime('%d.%m.%Y %H:%M')
        comment['date'] = comment_selector.xpath('//span[@class="greydate"]/text()').extract_first()
        comment['user_name'] = comment_selector.xpath('//p[@class="user"]/a/text()').extract_first()
        comment['user_link'] = comment_selector.xpath('//p[@class="user"]/a/@href').extract_first()
        comment['upvotes'] = comment_selector.xpath('//div[@class="pos"]/text()').extract_first()
        comment['downvotes'] = comment_selector.xpath('//div[@class="vote_area_v2"]/div[@class="neg"]/text()').extract_first()
        comment['content'] = comment_selector.xpath('//p[@class="text"]/text()').extract_first()

        return comment

    def get_answers(self, answer_selectors):
        answerArray = []
        if answer_selectors:
            for answer_selector in answer_selectors:
                answerArray.append(self.create_comment(None, answer_selector))
        return answerArray
