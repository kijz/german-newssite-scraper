# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from comments_scraper.items import CommentItem
import time
import datetime

class FocusSpider(scrapy.Spider):
    name = 'focus'
    allowed_domains = ['focus.de']
    #start_urls = ['http://focus.de/']
    custom_settings = {"DOWNLOADER_MIDDLEWARES": {'comments_scraper.middlewares.JSMiddleware': 543,},}
    start_urls = ['http://www.focus.de/politik/videos/zdf-moderatorin-nachdenklich-dunja-hayali-zu-konstanz-und-hamburg-mein-geduldsfaden-ist-duenner-geworden_id_7420014.html']

    #rules = [
    #    Rule(LinkExtractor(allow=['\/\w*\/\w*\/[\w*-]*.html']),
    #    callback='parse_site',
    #    follow=True)
    #]

    def parse(self, response):
        selector_list = response.css('div.comment')
        article_link = response.url

        for selector in selector_list:
            yield self.create_comment(article_link, selector)

    def parse_site(self, response):
        print (response.body)

        #selector_list = response.css('div.comment')
        #article_link = response.url

        #for selector in selector_list:
        #    comment = self.create_comment(article_link, selector)
        #    yield comment

    def create_comment(self, article_link, comment_selector):
        time_scraped = time.time()

        comment = CommentItem()
        comment['article_link'] = article_link
        comment['scraped_time_stamp'] = datetime.datetime.fromtimestamp(time_scraped).strftime('%d.%m.%Y %H:%M')
        comment['date'] = comment_selector.xpath('.//span[@class="greydate"]/text()').extract_first()
        comment['user_name'] = comment_selector.xpath('.//p[@class="user"]/a/text()').extract_first()
        comment['user_link'] = comment_selector.xpath('.//p[@class="user"]/a/@href').extract_first()
        comment['upvotes'] = comment_selector.xpath('.//div[@class="vote_area_v2"]/div').extract()[2]
        comment['upvotes'] = comment_selector.xpath('.//div[@class="vote_area_v2"]/div').extract()[4]
        comment['content'] = comment_selector.xpath('.//p[@class="text"]/text()').extract_first()

        '''
        check if comment has the "allAnwers" link, if yes, new request and parse the answers
        '''
        return comment

    def get_answers(self, answer_selectors):
        answerArray = []
        if answer_selectors:
            for answer_selector in answer_selectors:
                answerArray.append(self.create_comment(None, answer_selector))
        return answerArray
